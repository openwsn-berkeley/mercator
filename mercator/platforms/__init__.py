import yaml

class Platform(object):
    def __init__(self, config, *args):
        raise NotImplementedError()

    def setup_measurement(self, config):
        raise NotImplementedError()

    @classmethod
    def dump_sample_yml_file(cls):
        cls._dump_config_measurement()
        cls._dump_config_platform()

    @staticmethod
    def _dump_config_measurement():
        config = {}
        config['num_transactions'] = 10
        config['channels'] = [11, 12, 13, 14, 15, 16, 17, 18,
                              19, 20, 21, 22, 23, 24, 25, 26]
        config['tx_len'] = 100
        config['tx_interval_ms'] = 10
        config['tx_num_per_transaction'] = 100
        config['tx_fill_byte'] = 0x5a

        print(yaml.dump({'measurement': config}, default_flow_style=False))

    @staticmethod
    def _dump_config_platform():
        raise NotImplementedError
