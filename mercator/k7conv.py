import argparse
import gzip
import json
import os
from statistics import mean

def _find_node_list_and_end_time(raw_file_path):
    node_list = {}
    end_time = None
    with gzip.open(raw_file_path, 'rt') as raw_file:
        for line in raw_file:
            line = json.loads(line)
            if line['data_type'] == 'node_info':
                node_list[line['data']['mac_addr']] = line['data']['node_index']
            elif line['data_type'] == 'end_time':
                end_time = line['data']['timestamp']
                break
    return node_list, end_time

def _read_tx_line(line):
    line = json.loads(line)
    if line['data_type'] != 'tx':
        raise ValueError('data_type ({0})is not "tx"'.format(line['data_type']))
    data = line['data']
    return data['mac_addr'], data['datetime'], data['channel']

def _read_rx_lines(lines_to_read, node_list, tx_count):
    tuples_to_output = []
    for line in lines_to_read:
        line = json.loads(line)
        assert line['data_type'] == 'rx'

        data = line['data']
        rx_mac_addr = data['mac_addr']
        rssi_records = data['rssi_records']
        rx_node_id = node_list[rx_mac_addr]

        # compute mean RSSI and PDR
        valid_rssi_values = [rssi for rssi in rssi_records if rssi]
        rx_count = len(valid_rssi_values)
        pdr = rx_count / tx_count
        if pdr > 0:
            mean_rssi = mean(valid_rssi_values)
        else:
            mean_rssi = None

        # save to the file
        tuples_to_output.append((rx_node_id, mean_rssi, pdr))

    return tuples_to_output

def _generate_k7_header(location, config, start_time, end_time):
    header = {}
    header['location'] = location
    header['tx_length'] = config['measurement']['tx_len']
    header['start_date'] = start_time
    header['stop_date'] = end_time
    header['node_count'] = len(config['platform']['nodes'])
    header['channels'] = config['measurement']['channels']
    header['interframe_duration'] = config['measurement']['tx_interval_ms']
    return json.dumps(header) + '\n'

def convert_raw_file(location, raw_file_path, out_file_path):
    CSV_HEADER = 'datetime,src,dst,channel,mean_rssi,pdr,tx_count\n'
    start_time = None
    node_list, end_time = _find_node_list_and_end_time(raw_file_path)
    if not end_time:
        raise ValueError('Invalid raw file format {0}; '.format(raw_file_path)
                         + '"end_time" data is not found')
    with gzip.open(out_file_path, 'wt') as out_file:
        with gzip.open(raw_file_path, 'rb') as raw_file:
            # read config line
            line = json.loads(raw_file.readline())
            assert line['data_type'] == 'config'
            config = line['data']

            # shorthand
            tx_count = config['measurement']['tx_num_per_transaction']
            num_nodes = len(config['platform']['nodes'])

            # read start time, and insert headers
            line = json.loads(raw_file.readline())
            assert line['data_type'] == 'start_time'
            start_time = line['data']['timestamp']
            header_line = _generate_k7_header(location, config,
                                              start_time, end_time)
            out_file.write(header_line)
            out_file.write(CSV_HEADER)

            # read start of transaction
            for line in raw_file:
                try:
                    tx_mac_addr, timestamp, channel = _read_tx_line(line)
                    tx_node_id = node_list[tx_mac_addr]
                except ValueError:
                    line = json.loads(line)
                    if line['data_type'] == 'end_time':
                        assert end_time == line['data']['timestamp']
                        break
                    elif line['data_type'] == 'node_info':
                        # skip
                        continue
                    else:
                        raise ValueError('The current line should be '
                                         + '"tx" or "end_time"')

                # read RX records
                lines_to_read = [raw_file.readline()
                                 for _ in range(num_nodes-1)]
                tuples_to_output = _read_rx_lines(lines_to_read,
                                                  node_list,
                                                  tx_count)
                for dst, mean_rssi, pdr in tuples_to_output:
                    mean_rssi = ('{0:.2f}'.format(mean_rssi)
                                 if mean_rssi else None)
                    out_file.write('{0},{1},{2},{3},'.format(timestamp,
                                                             tx_node_id,
                                                             dst,
                                                             channel)
                                   + '{0},{1},{2}\n'.format(mean_rssi,
                                                            pdr,
                                                            tx_count))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='location',
                        help='specify "location" to be shown in K7 header',
                        type=str, required=True)
    parser.add_argument('-o', dest='out_file_path',
                        help='path to a resulting K7 file (.k7.gz)',
                        default='output.k7.gz')
    parser.add_argument('-f', dest='force',
                        help='overwrite an existing K7 file (.k7.gz)',
                        action='store_true')
    parser.add_argument('raw_file_path',
                        help='path to a raw output file (.jsonl.gz) to convert')
    args = parser.parse_args()

    if not os.path.exists(args.raw_file_path):
        raise ValueError('{0} doesn\'t exist'.format(args.raw_file_path))
    elif (not args.force) and os.path.exists(args.out_file_path):
        raise ValueError('{0} exists'.format(args.out_file_path))
    else:
        convert_raw_file(args.location, args.raw_file_path, args.out_file_path)

if __name__ == '__main__':
    main()
