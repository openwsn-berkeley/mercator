import argparse
import datetime
from importlib import import_module
import logging
import logging.config
import math
import os
import signal
import sys
import threading
import time

import tqdm
import yaml

from mercator.node import NodeStatus

from mercator.utils import MercatorHalo, Outfile, print_bold

class SigIntException(Exception):
    pass

def _init_logger(config):
    try:
        logging.config.dictConfig(config)
    except yaml.YAMLError as err:
        print_bold('{0} is not a valid YAML file'.format(config_file_path))
        exit(1)
    except ValueError as err:
        print_bold('logging config is not loaded succesfully')
        print(str(err))
        exit(1)

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', dest='dump_sample_yml_file',
                        help='print sample YAML file for a specified platform',
                        choices=['iotlab', 'opentestbed'],
                        type=str)
    parser.add_argument('-c', dest='config', help='path to config YAML file',
                        type=str, default='./mercator.yml')
    parser.add_argument('-i', dest='exp_id',
                        help='attach to exp_id (only for iotlab)',
                        type=int)
    parser.add_argument('-p', dest='program_firmware',
                        help='program firmware to nodes (only for opentestbed)',
                        default=False, action='store_true')
    parser.add_argument('-o', dest='out_file_path',
                        help='path to an output file',
                        type=str, default='output.jsonl.gz')
    parser.add_argument('-f', dest='overwrite_out_file',
                        help='overwrite an existing file',
                        default=False, action='store_true')
    parser.add_argument('-s', '--only-platform-setup',
                        dest='only_platform_setup',
                        help='exit without measurements',
                        default=False, action='store_true')
    parser.add_argument('-q', dest='quiet',
                        help='suppress console outputs', action='store_true')
    return parser.parse_args()

def _read_config(config_file_path):
    if not os.path.exists(config_file_path):
        print_bold('{0} is not found'.format(config_file_path))
        print_bold('use -c option to specify the path to your mercator.yml')
        raise ValueError('mercator.yml is not found')

    with open(config_file_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as err:
            config_file_name = os.path.basename(config_file_path)
            print('cannot parse {0} as a YAML file'.format(config_file_name),
                  file=sys.stderr)
            print(err, file=sys.stderr)
            exit(1)

    # 'nodes' key may have a list of lists; flatten such a list
    for node_id_list in [config['platform']['nodes'],
                      config['measurement']['tx_nodes']]:
        assert node_id_list
        if isinstance(node_id_list[0], list):
            flattened_node_id_list = [node_id for node_id_sub_list in node_id_list
                                    for node_id in node_id_sub_list]
            if node_id_list == config['platform']['nodes']:
                config['platform']['nodes'] = flattened_node_id_list
            elif node_id_list == config['measurement']['tx_nodes']:
                config['measurement']['tx_nodes'] = flattened_node_id_list
            else:
                raise NotImplementedError()

    return config

def _setup_platform(platform_config, args):
    module_name = 'mercator.platforms.{0}'.format(platform_config['name'])
    platform_module = import_module(module_name)

    if platform_config['name'] == 'iotlab':
        platform_args = {'exp_id': args.exp_id}
    elif platform_config['name'] == 'opentestbed':
        platform_args = {'program_firmware': args.program_firmware}
    else:
        raise NotImplementedError(
            'Platform {0} is not supported'.format(platform_config['name']))

    return  platform_module.Platform(platform_config, **platform_args)

def _run_transactions(num_transactions, channels, nodes, outfile, quiet):
    quit_now = False

    def _sigint_handler(sig, frame):
        raise SigIntException()

    def _running_in_thread():
        tx_nodes = [node for node in nodes if node.tx_node]
        num_tx_nodes = len(tx_nodes)
        total_exec_num = num_transactions * len(channels) * num_tx_nodes
        params = _get_measurement_params(num_transactions, channels,
                                         num_tx_nodes)

        with tqdm.tqdm(total=total_exec_num, unit='meas', disable=quiet) as pbar:
            for trans_ctr, channel, tx_node_idx in params:
                tx_node = tx_nodes[tx_node_idx]
                _beginning_of_measurement(pbar,
                                          trans_ctr, channel,
                                          tx_node_idx, num_tx_nodes)
                try:
                    _do_measurement(nodes, tx_node, trans_ctr, channel, outfile)
                except RuntimeError:
                    print_bold('RuntimeError occurs; stopping Mercator...')
                    break

                _end_of_measurement(pbar,
                                    trans_ctr, channel,
                                    tx_node_idx, num_tx_nodes)
                if quit_now:
                    break

    signal.signal(signal.SIGINT, _sigint_handler)
    thread = threading.Thread(target=_running_in_thread)
    try:
        thread.start()
        thread.join()
    except (KeyboardInterrupt, SigIntException):
        quit_now = True
        print_bold('KeyboardInterrupt/SIGINT is received; Mercator will stop.')
        print_bold('Waiting for the current measurement to finish...')
        thread.join()

def _get_measurement_params(num_transactions, channels, num_tx_nodes):
    trans_ctr = 0
    while trans_ctr < num_transactions:
        for channel in channels:
            for node_idx in range(num_tx_nodes):
                yield trans_ctr, channel, node_idx
        trans_ctr += 1

def _do_measurement(nodes, tx_node, trans_ctr, channel, outfile):
    rx_nodes = [node for node in nodes if node != tx_node]
    start_time_of_measurement = datetime.datetime.now()

    if not _is_every_node_idle(nodes):
        raise RuntimeError('NodeStatus Error')

    _make_rx_nodes_start_listening(rx_nodes,
                                   tx_node, channel, trans_ctr)

    # start TX and wait to finish
    tx_node.start_tx(channel, trans_ctr)
    tx_node.wait_tx_done()

    _make_rx_nodes_stop_listening(rx_nodes)
    _save_data(outfile, tx_node, rx_nodes,
               start_time_of_measurement, trans_ctr, channel)

    outfile.flush()

def _beginning_of_measurement(pbar, trans_ctr, channel, node_idx, num_nodes):
    logging.info('Beginning of measurement - '
                 + 'trans_ctr: {0}, '.format(trans_ctr)
                 + 'channel: {0}, '.format(channel)
                 + 'tx_node: {0}/{1}'.format(node_idx+1,
                                             num_nodes))

    pbar.set_description('trans_ctr {0}'.format(trans_ctr))
    pbar.set_postfix(ch=channel,
                     tx_node='{0}/{1}'.format(node_idx+1,
                                              num_nodes))

def _is_every_node_idle(nodes):
    ret = True
    threads = {}
    for _idx, _node in enumerate(nodes):
        thread = threading.Thread(target=_node.update_status)
        thread.start()
        threads[_idx] = thread
    for _idx, _node in enumerate(nodes):
        threads[_idx].join()
        if _node.status != NodeStatus.IDLE:
            logging.critical('Invalid NodeStatus at '
                             + 'Node {0} '.format(_node.id)
                             + '{0}'.format(_node.status.name))
            ret = False
    return ret

def _make_rx_nodes_start_listening(rx_nodes, tx_node, channel, trans_ctr):
    threads = {}
    for _idx, _node in enumerate(rx_nodes):
        thread = threading.Thread(target=_node.start_rx,
                                  args=(channel,
                                        tx_node.mac_addr,
                                        trans_ctr))
        thread.start()
        threads[_idx] = thread
    for _idx, _node in enumerate(rx_nodes):
        threads[_idx].join()

def _make_rx_nodes_stop_listening(rx_nodes):
    threads = {}
    for _idx, _node in enumerate(rx_nodes):
        thread = threading.Thread(target=_node.stop_rx)
        thread.start()
        threads[_idx] = thread
    for _idx, _node in enumerate(rx_nodes):
        threads[_idx].join()

def _save_data(outfile, tx_node, rx_nodes, start_time, trans_ctr, channel):
    outfile.write_data('tx',
                       {'datetime': start_time.isoformat(),
                        'trans_ctr': trans_ctr,
                        'channel': channel,
                        'mac_addr': str(tx_node.mac_addr)})
    for rx_node in rx_nodes:
        rx_data = {'mac_addr': str(rx_node.mac_addr),
                   'rssi_records': rx_node.rssi_records}
        outfile.write_data('rx', rx_data)

def  _end_of_measurement(pbar, trans_ctr, channel, node_idx, num_nodes):
    logging.info('End of measurement - '
                 + 'trans_ctr: {0}, '.format(trans_ctr)
                 + 'channel: {0}, '.format(channel)
                 + 'tx_node: {0}/{1}'.format(node_idx+1,
                                             num_nodes))
    pbar.update()

def main():
    args = _parse_args()

    if args.dump_sample_yml_file:
        module_name = 'mercator.platforms.{0}'.format(args.dump_sample_yml_file)
        platform_module = import_module(module_name)
        platform_module.Platform.dump_sample_yml_file()
    elif args.config:
        if args.quiet:
            print_bold('-q ("quiet") is specified. ' +
                       'See mercator.log for mercator\'s activities.')
            MercatorHalo.disable()

        config = _read_config(args.config)
        _init_logger(config['logging'])
        outfile = Outfile(args.out_file_path, config, args.overwrite_out_file)

        logging.info('Start Mercator at '
                     + '"{0}" platform'.format(config['platform']['name']))

        platform = _setup_platform(config['platform'], args)
        nodes = platform.setup_measurement(config['measurement'])

        if args.only_platform_setup:
            # done
            pass
        else:
            channels = config['measurement']['channels']
            num_transactions = config['measurement']['num_transactions']

            if num_transactions < 0:
                # if we have a negative value, take it as an infinite
                # value
                num_transactions = math.inf

            # body of main
            outfile.open()
            outfile.write_data('start_time',
                               {'timestamp': datetime.datetime.now().isoformat()})
            _run_transactions(num_transactions, channels, nodes, outfile,
                              args.quiet)
            for node_idx, node in enumerate(nodes):
                outfile.write_data('node_info', {'node_index': node_idx,
                                                 'mac_addr': str(node.mac_addr)})
            outfile.write_data('end_time',
                               {'timestamp': datetime.datetime.now().isoformat()})
            outfile.close()
    else:
        raise ValueError('Shouldn\'t come here')

if __name__ == '__main__':
    main()
