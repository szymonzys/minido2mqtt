#!/usr/bin/env python
import sys

from twisted.internet import reactor
from twisted.python import usage

from mqttminidoservice import MQTTBridgeServiceOptions, MQTTBridgeService, BridgeHandler


# -----------------------
# MQTT Low Level Bridge Service
# ------------------------

class MQTTLowService(MQTTBridgeService, BridgeHandler):
    def __init__(self, config):
        MQTTBridgeService.__init__(self, config)
        BridgeHandler.__init__(self, False)



        self.subscribeTopics.append(self.topicLowWrite)

    def onPublish(self, topic, payload, qos, dup, retain, msgId):
        '''
        Callback Receiving messages from publisher
        '''
        self.receievedMessage(payload)

    def printMessage(self, message):
        print("RECIEVED: msg={payload}".format(payload=message))

    def sendMessage(self, message):
        b = bytearray()
        b.extend(message)
        self.publish(self.topicLowRead, b, self.qos, False)

if __name__ == '__main__':
    config = MQTTBridgeServiceOptions()

    try:
        config.parseOptions()  # When given no argument, parses sys.argv[1:]
    except usage.UsageError as errortext:
        print('{}: {}'.format(sys.argv[0], errortext))
        print('{}: Try --help for usage details.'.format(sys.argv[0]))
        sys.exit(1)


    serv       = MQTTLowService(config)
    serv.startService()
    reactor.run()