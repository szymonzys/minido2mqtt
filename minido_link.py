#!/usr/bin/env python
import sys

from twisted.application.service import MultiService
from twisted.python import usage
from twisted.internet import reactor

from minidoservice import MinidoService, MinidoServiceOptions
from mqttlowservice import MQTTLowService
from mqttminidoservice import MQTTBridgeServiceOptions, BridgeDelegate


class BridgeOptions(MinidoServiceOptions, MQTTBridgeServiceOptions):
    pass

class BridgeService(MultiService):
    def __init__(self, config):
        MultiService.__init__(self)
        self.minido = MinidoService(config)
        self.addService(self.minido)

        self.mqtt = MQTTLowService(config)
        self.addService(self.mqtt)

        self.minido.onReceivedDelegate = BridgeDelegate(self.mqtt)
        self.mqtt.onReceivedDelegate = BridgeDelegate(self.minido)

if __name__ == "__main__":
    config = BridgeOptions()
    try:
        config.parseOptions()  # When given no argument, parses sys.argv[1:]
    except usage.UsageError as errortext:
        print('{}: {}'.format(sys.argv[0], errortext))
        print('{}: Try --help for usage details.'.format(sys.argv[0]))
        sys.exit(1)


    service = BridgeService(config)
    service.startService()
    reactor.run()

