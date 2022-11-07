#!/usr/bin/env python
import sys
from datetime import datetime

from twisted.internet import reactor
from twisted.python import usage


from minidomodel import MinidoModel
from minidopackage import MINIDO, CMD, STATUS, ExiStatusPdu, MiniPduFactory, strHex, ExoUpdatePdu, EndPoint, CommandPdu
from minidoservice import MinidoOptions
from mqtthomedevice import MinidoHomeDevice, ExiDevice, ExoDevice
from mqttminidoservice import MQTTBridgeServiceOptions, MQTTBridgeService
from mqtthomeprotocol import MQTTHomeProtocol

class MQTTHomeServiceOptions(MQTTBridgeServiceOptions, MinidoOptions):
    optParameters = [
        ["mqttId", "i", "minidohome", "Id to use for this MQTT client"],
        ["homeTopic", None, "home", "MQTT topic element for home bus message"],
        ["discoveryTopic", None, "homeassistant", "MQTT topic for discovery service"]
    ]

    optFlags = [
        ["low", "l", "Verbose low level protocol"],
    ]

# -----------------------
# MQTT Low Level Bridge Service
# ------------------------

class MQTTHomeService(MQTTBridgeService):
    def __init__(self, config):
        MQTTBridgeService.__init__(self, config)
        self.filtering = config['filter']
        self.verbose = config['verbose']
        self.verboseLow = config['low']

        #TODO: low and home topics must be diffrent
        self.topicHome = self.topicMinido + config["homeTopic"] + "/"
        self.topicDiscovery = config["discoveryTopic"] + "/"
        self.subscribeTopics.append(self.topicMinido + "#")

        #self.lastmsgtime = datetime.datetime.now()

        self.pduFactory = MiniPduFactory()
        self.model = MinidoModel()
        self.devices = []
        self.homeProtocol = MQTTHomeProtocol(self)
        self.devices.append(MinidoHomeDevice(self.homeProtocol))
        self.devices.append(ExiDevice(self.homeProtocol))
        self.devices.append(ExoDevice(self.homeProtocol))



    def onPublish(self, topic, payload, qos, dup, retain, msgId):
        if topic.startswith(self.topicLow):
            self.processLowLevelMessage(topic, payload, qos, dup, retain, msgId)
        else:
            if topic.startswith(self.topicHome):
                self.processHomeLevelMessage(topic, payload, qos, dup, retain, msgId)


    def processLowLevelMessage(self, topic, payload, qos, dup, retain, msgId):
        packet = self.pduFactory.createPdu(payload)
        self.printPacket(packet)

        for dev in self.devices:
            if dev.isMyPdu(packet):
                dev.handleLowPdu(packet)



    def sendPackage(self, packet):
        pdu = packet.getpdu()
        b = bytearray()
        b.extend(pdu)
        self.publish(self.topicLowWrite, b, None, False)

    def printPacket(self, packet, prefix="@LOW: "):
        if self.verboseLow and not (self.filtering and CMD.ignoreCMD(packet.command)):
            print(prefix + str(packet) + " PDU:" + strHex(packet.chardata))

    def processHomeLevelMessage(self, topic, payload, qos, dup, retain, msgId):
        self.homeProtocol.homeLevelMessageReceived(topic, payload)

if __name__ == '__main__':
    config = MQTTHomeServiceOptions()

    try:
        config.parseOptions()  # When given no argument, parses sys.argv[1:]
    except usage.UsageError as errortext:
        print('{}: {}'.format(sys.argv[0], errortext))
        print('{}: Try --help for usage details.'.format(sys.argv[0]))
        sys.exit(1)


    serv       = MQTTHomeService(config)
    serv.startService()
    reactor.run()