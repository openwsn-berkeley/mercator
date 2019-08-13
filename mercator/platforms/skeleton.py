import mercator.node
import mercator.platforms

class Platform(mercator.platforms.Platform):
    def __init__(self, config, *args):
        # 'args' is platform-specific arguments; see iotlab.py or
        # opentestbed.py for your reference
        raise NotImplementedError()

    def setup_measurement(self, config):
        raise NotImplementedError()

class Node(mercator.node.Node):
    def __init__(self, platform, *args):
        # 'args' is platform-specific arguments; see iotlab.py or
        # opentestbed.py for your reference

        # MUST BE CALLED
        super(Node, self).__init__(platform)

        raise NotImplementedError()

    def _setup(self):
        raise NotImplementedError()

    def _platform_send(self):
        raise NotImplementedError()

    def _platform_recv(self):
        raise NotImplementedError()
