"""https://www.iot-lab.info
https://www.iot-lab.info/tutorials/submit-experiment-m3-clitools/
"""

import datetime
import hashlib
import json
import logging
import os
import re
import socket
import sys
import threading
import time

import dateutil.parser
import dateutil.tz
import iotlabcli.auth
import iotlabcli.parser.auth
import iotlabclient.client
import websocket
import yaml

from mercator.hdlc import HDLC_FLAG
import mercator.node
import mercator.platforms
from mercator.utils import print_bold, MercatorHalo, OSName

LOCAL_IP_ADDRESS = '127.0.0.1'
IOT_LAB_DOMAIN_NAME = 'iot-lab.info'

class Platform(mercator.platforms.Platform):
    POOLING_INTERVAL_SECONDS = 5

    def __init__(self, config, exp_id):
        # make sure we have the user credentials saved locally
        self.username, password = self._get_credentials()

        # collect nodes and identify the test site
        self.nodes = [Node(self, hostname) for hostname in config['nodes']]
        sites = set([node.site for node in self.nodes])
        if len(sites) == 0:
            raise ValueError('Invalid format for nodes in yml file')
        elif len(sites) > 1:
            raise ValueError('Cannot use nodes over multiple sites')
        self.site = sites.pop()

        # setup iot-lab-client instance
        client_configuration = iotlabclient.client.Configuration()
        client_configuration.username = self.username
        client_configuration.password = password
        self.api_client = iotlabclient.client.ApiClient(client_configuration)

        # collect experiment settings
        self.exp_id = exp_id
        self.experiment_duration_min = config['experiment_duration_min']
        self.firmware_name = self._prepare_firmware(config['firmware'])
        self.firmware_os_name = OSName(config['firmware']['os'].lower())
        self.token = None

    def setup_measurement(self, config):
        # make sure we don't have an active experiment of the same
        # configuration
        experiment_name = self._get_experiment_name()

        # submit an experiment
        if self.exp_id:
            if self.exp_id != self._get_exp_id(experiment_name):
                print_bold('exp_id {0} is not found on the system'.format(
                    self.exp_id)
                )
                print_bold('Retry without -i {0} option'.format(self.exp_id))
                exit(1)
        else:
            self.exp_id = self._submit_experiment(experiment_name, config)

        # wait until the experiment is scheduled
        scheduled_date = self._get_scheduled_date()

        # wait until the experiment get started
        self._wait_until_experiment_starts(scheduled_date)

        # reset the nodes
        self._reset_nodes()

        # get a token for WebSocket
        self.token = self._get_token()

        # setting up nodes
        self._setup_nodes(config)

        return self.nodes

    @staticmethod
    def _dump_config_platform():
        config = {}
        config['name'] = 'iotlab'
        config['duration_min'] = 60
        config['nodes'] = ['m3-x.site.iot-lab.info',
                           'm3-y.site.iot-lab.info',
                           'm3-z.site.iot-lab.info']
        config['firmware'] = {}
        config['firmware']['os'] = 'OpenWSN'
        config['firmware']['archi'] = 'M3'
        config['firmware']['path'] = 'firmwares/openwsn-iot-lab_M3.elf'

        print(yaml.dump({'platform': config}, default_flow_style=False))

    @staticmethod
    def _get_credentials():
        if not os.path.exists(iotlabcli.auth.RC_FILE):
            username = input('User Name of FIT/IoT-LAB: ')
            sys.stdout.flush()
            parser = iotlabcli.parser.auth.parse_options()
            opts = parser.parse_args(['-u', username])
            try:
                assert (iotlabcli.parser.auth.auth_parse_and_run(opts)
                        == 'Written')
            except RuntimeError as err:
                assert str(err) == 'Wrong login:password'
                print_bold('Login failed')
                print('Wrong login username and/or password')
                exit(1)

        spinner = MercatorHalo(text='Identifying credentials for FIT/IoT-LAB')
        username, password = iotlabcli.auth.get_user_credentials()
        if not password:
            spinner.stop_failure()
            print_bold('Password is empty, something worng')
            print('Removing {0}, and exit'.format(iotlabcli.auth.RC_FILE))
            os.remove(iotlabcli.auth.RC_FILE)
            exit(1)
        else:
            spinner.stop_success()

        return username, password

    def _setup_nodes(self, config):
        spinner = MercatorHalo(text='Setting up nodes')

        threads = []
        for node in self.nodes:
            thread = threading.Thread(target=node.setup, args=(config,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        # all the nodes should be IDLE
        for node in self.nodes:
            if node.status != mercator.node.NodeStatus.IDLE:
                spinner.stop_failure()
                print_bold('Node {0} has an invalid status '.format(node.id)
                           + '{0}'.format(node.status))
                exit(1)
        spinner.stop_success()

    def _prepare_firmware(self, firmware):
        archi_label = firmware['archi'].upper()
        firmware_archi = getattr(iotlabclient.client.ArchiString, archi_label)
        firmware_name = os.path.basename(firmware['path'])
        firmware_metadata = iotlabclient.client.Firmware(
            name=firmware_name,
            description='Mercator Firmware for {0}'.format(archi_label),
            archi=firmware_archi,
            filename=firmware_name
        )

        if self.exp_id:
            # if we have a concrete exp_id now, we don't need to
            # upload the firmware
            pass
        else:
            spinner = MercatorHalo(
                text='Saving the firmware, "{0}", to FIT/IoT-LAB'.format(
                    firmware_name))
            api = iotlabclient.client.FirmwaresApi(self.api_client)
            # first, check the archi
            if firmware_archi == iotlabclient.client.ArchiString.A8:
                # FIT/IoT-LAB doesn't support WebSocket For A8, which
                # Mercator needs to run
                spinner.stop_failure()
                print_bold('A8 is not supported by Mercator')
                exit(1)

            # second, delete a firmware having the same name if exists
            try:
                api.delete_firmware(firmware_name)
            except iotlabclient.client.rest.ApiException as err:
                assert(err.status == 500)

            # third, save the firmware to the system
            try:
                api.save_firmware(firmware=firmware['path'],
                                  metadata=firmware_metadata)
                spinner.stop_success()
            except iotlabclient.client.rest.ApiException as err:
                err_body = json.loads(err.body)
                spinner.stop_failure()
                print_bold('Failed to save the firmware '
                           + '{0}'.format(firmware_name))
                print('{0}, {1}'.format(err.reason, err_body['message']))
                exit(1)
        return firmware_name

    def _submit_experiment(self, experiment_name, config):
        spinner = MercatorHalo(text='Submitting an experiment')
        # make sure there is no experiment registered for the same
        # config
        exp_id = self._get_exp_id(experiment_name)
        if exp_id:
            spinner.stop_failure()
            print_bold('Found a registered experiment having the same name.')
            print('The name of the experiment is "{0}", its ID is {1}'.format(
                experiment_name, exp_id))
            print('Check the active experiments on '
                  + 'https://www.iot-lab.info/testbed/dashboard\n'
                  + 'To see status of the registered experiment, run:\n'
                  + '    $ iotlab-experiment get -i {0} -p'.format(exp_id))
            print('To stop the registered experiment:\n'
                  + '    $ iotlab-experiment stop -i {0}'.format(exp_id))
            exit(1)

        # experiment submission
        node_list = [node.hostname for node in self.nodes]
        experiment = iotlabclient.client.ExperimentPhysical(
            duration=self.experiment_duration_min,
            name=experiment_name,
            nodes=node_list,
            firmwareassociations=[
                iotlabclient.client.FirmwareAssociation(
                    firmwarename=self.firmware_name,
                    nodes=node_list)])
        api = iotlabclient.client.ExperimentsApi(self.api_client)
        try:
            # res is an InlineResponse200 instance
            res = api.submit_experiment(experiment=experiment)
            exp_id = res.id
            spinner.stop_success()
            print_bold('Experiment ID is {0}'.format(exp_id))
        except iotlabclient.client.rest.ApiException as err:
            err_body = json.loads(err.body)
            spinner_stop_failure()
            print('{0}, {1}'.format(err.reason, err_body['message']))
            exit(1)
        return exp_id

    def _get_scheduled_date(self):
        spinner = MercatorHalo(text='Waiting to be scheduled')
        api = iotlabclient.client.ExperimentApi(self.api_client)
        while True:
            try:
                res = api.get_experiment(self.exp_id)
            except iotlabclient.client.rest.ApiException as err:
                spinner.stop_failure()
                print_bold(
                    'Cannot get info of experiment {0}'.format(self.exp_id))
                exit(1)
            submission_date = dateutil.parser.parse(res.submission_date)
            scheduled_date = dateutil.parser.parse(res.scheduled_date)
            if ((res.state in ['Running', 'Launching', 'toLaunch'])
                or (res.state == 'Waiting'
                    and submission_date < scheduled_date)):
                spinner.stop_success()
                print_bold('Scheduled at {0}'.format(
                    scheduled_date.astimezone(dateutil.tz.tzlocal())))
                break
            elif (res.state not in
                  ['Running', 'Launching', 'toLaunch', 'Waiting']):
                spinner.stop_failure()
                message = 'Experiment {0} has an invalid state {1}'.format(
                    self.exp_id, res.state)
                print_bold('Invalid state: {0}'.format(res.state))
                exit(1)
            time.sleep(self.POOLING_INTERVAL_SECONDS)
        return scheduled_date

    def _get_token(self):
        spinner = MercatorHalo(text='Getting a token')

        # get a token
        assert self.exp_id
        api = iotlabclient.client.ExperimentApi(self.api_client)
        try:
            res = api.get_experiment_token(self.exp_id)
            token = res.token
        except iotlabclient.client.rest.ApiException as err:
            err_body = json.loads(err.body)
            spinner.stop_failure()
            print_bold('Failed to get a token')
            print('{0}, {1}'.format(err.reason, err_body['message']))
            exit(1)

        spinner.stop_success()
        return token

    def _wait_until_experiment_starts(self, scheduled_date):
        spinner = MercatorHalo(text='Waiting to start')
        now = datetime.datetime.now(dateutil.tz.tzutc())
        if scheduled_date < now:
            # the experiment should have started already
            pass
        else:
            delta_seconds = (now - scheduled_date).seconds
            time.sleep(delta_seconds)

        api = iotlabclient.client.ExperimentApi(self.api_client)
        while True:
            try:
                res = api.get_experiment(self.exp_id)
            except iotlabclient.client.rest.ApiException as err:
                spinner.stop_failure()
                print_bold(
                    'Cannot get info of experiment {0}'.format(self.exp_id))
                exit(1)

            if res.state == 'Running':
                spinner.stop_success()
                break
            elif res.state not in ['Launching', 'toLaunch', 'Waiting']:
                # the experiment shouldn't be waiting after the
                # scheduled date
                spinner.stop_failure()
                message = 'Experiment {0} has an invalid state {1}'.format(
                    self.exp_id, res.state)
                print_bold('Invalid state: {0}'.format(res.state))
                exit(1)
            time.sleep(self.POOLING_INTERVAL_SECONDS)

    def _reset_nodes(self):
        spinner = MercatorHalo(text='Resetting nodes')
        api = iotlabclient.client.ExperimentApi(self.api_client)
        try:
            res = api.send_cmd_nodes(self.exp_id, 'reset')
        except iotlabclient.client.rest.ApiException as err:
            spinner.stop_failure()
            print_bold('Cannot reset the nodes for experiment '
                       + '{0}'.format(self.exp_id))
            exit(1)
        # not sure how to check 'res' of reset command... :(
        spinner.stop_success()


    def _get_exp_id(self, experiment_name):
        api = iotlabclient.client.ExperimentsApi(self.api_client)
        res = api.get_experiments(state='Running,Launching,toLaunch,Waiting')
        exp_id = None
        for experiment in res.items:
            if experiment.name == experiment_name:
                exp_id = experiment.id

        return exp_id

    def _get_experiment_name(self):
        m = hashlib.sha1()
        m.update(self.firmware_name.encode('utf-8'))
        node_list = sorted([node.hostname for node in self.nodes])
        m.update(','.join(node_list).encode('utf-8'))
        return 'Mercator_{0}'.format(m.hexdigest()[:7])

class Node(mercator.node.Node):
    TCP_PORT_TO_SERIAL = 20000
    WS_TIMEOUT_SECONDS = 3

    def __init__(self, platform, hostname):
        super(Node, self).__init__(platform)

        # 'hostname' is a string like "m3-1.grenoble.iot-lab.info"
        self.hostname = hostname
        self.id, self.site = re.sub(r'\.{0}$'.format(IOT_LAB_DOMAIN_NAME),
                                    '', self.hostname).split('.')
        self.ws = None

    def _setup(self):
        # open a WebSocket
        self.ws = self._open_ws()
        self.ws.settimeout(self.WS_TIMEOUT_SECONDS)

    def _am_i_tx_node(self, tx_nodes):
        full_node_id = '{0}.{1}.{2}'.format(self.id, self.site,
                                            IOT_LAB_DOMAIN_NAME)
        return full_node_id in tx_nodes

    def _open_ws(self):
        # short-hands
        username = self.platform.username
        exp_id = self.platform.exp_id
        site = self.platform.site
        token = self.platform.token

        assert username
        assert exp_id
        assert site
        assert token
        ws = websocket.WebSocket()
        url = 'wss://www.iot-lab.info:443/ws/{0}/{1}/{2}/serial/raw'.format(
            site, exp_id, self.id)
        try:
            ws.connect(url, subprotocols=[username, 'token', token])
        except websocket.WebSocketBadStatusException as err:
            raise RuntimeError('{0}, {1}'.format(url, str(err)))
        return ws

    def _platform_send(self, msg):
        try:
            self.ws.send_binary(msg)
        except (websocket.WebSocketConnectionClosedException, BrokenPipeError):
            self._handle_connection_lost()

    def _platform_recv(self):
        try:
            data = self.ws.recv()
        except websocket.WebSocketTimeoutException as err:
            logging.debug('Recv on WebSocket from {0} timeout'.format(self.id))
            data = b''
        except websocket.WebSocketConnectionClosedException:
            self._handle_connection_lost()
            data = b''

        return data

    def _handle_connection_lost(self):
        # we lost the connection; change the node's status to UNKNOWN.
        logging.critical('Connection to {0} is closed'.format(self.id))
        self.status = mercator.node.NodeStatus.UNKNOWN
        # Mercator will stop
