import datetime

from mqtt.client.factory import MQTTFactory
from twisted.application.internet import ClientService, backoffPolicy
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.internet.endpoints import clientFromString
from twisted.python import usage

from minidopackage import strHex


def qosRange(val):
    val = int(val)
    if val not in range(0, 3):
        raise ValueError("Not in range")
    return val
qosRange.coerceDoc = "Must be 0, 1, or 2."

class MQTTOptions(usage.Options):
    optParameters = [
        ["mqttBroker", "b", "192.168.1.230", "MQTT Broker address"],
        ["mqttPort", "r", 1883, "MQTT Broker port"],
        ["mqttUser", "U", "mqtt", "MQTT Broker authentication user name"],
        ["mqttPassword", "P", "mqtt", "MQTT Broker authentication password"],
        ["mqttId", "i", "minidolink", "Id to use for this MQTT client"],
        ["mqttKeepAlive", "k", 60, "Keep alive in seconds for this MQTT client", int],
        ["mqttQoS", "q", 0, "Quality of service for MQTT messages for minido messages", qosRange]
    ]


class MQTTMinidoBaseServiceOptions(MQTTOptions):
    optParameters = [
        ["mqttTopic", "t", "minido", "MQTT topic name prefix for minido messages"],
        ["mqttHomeId", "h", "myhome", "MQTT topic name home identifier for minido messages"]

    ]


class MQTTMinidoBaseService(ClientService):
    def __init__(self, config):
        ClientService.__init__(self, clientFromString(reactor, "tcp:" + config["mqttBroker"] + ":" + str(config["mqttPort"])),
                               MQTTFactory(MQTTFactory.SUBSCRIBER | MQTTFactory.PUBLISHER),
                               retryPolicy=backoffPolicy())

        self.broker = "tcp:" + config["mqttBroker"] + ":" + str(config["mqttPort"])
        self.username = config["mqttUser"]
        self.password = config["mqttPassword"]
        self.clientId = config["mqttId"]
        self.keepAlive = config["mqttKeepAlive"]
        self.qos = config["mqttQoS"]
        self.subscribeTopics = list()


    def onDisconnection(self, reason):
        '''
        get notfied of disconnections
        and get a deferred for a new protocol object (next retry)
        '''
        print(" >< Connection was lost ! ><, reason={r}".format(r=reason))
        self.whenConnected().addCallback(self.connectToBroker)

    @inlineCallbacks
    def connectToBroker(self, protocol):
        '''
        Connect to MQTT broker
        '''
        self.protocol = protocol
        self.protocol.onPublish = self.onPublish
        self.protocol.onDisconnection = self.onDisconnection
        self.protocol.setWindowSize(1)

        try:
            yield self.protocol.connect(self.clientId, self.keepAlive,
                                        username=self.username, password=self.password)
            yield self.subscribe()
        except Exception as e:
            print("Connecting to {broker} raised {excp!s}".format(
                broker=self.broker, excp=e))
        else:
            print("Connected and subscribed to " + self.broker)


    def startService(self):
        print("Starting MQTT Service")
        # invoke whenConnected() inherited method
        self.whenConnected().addCallback(self.connectToBroker)
        ClientService.startService(self)

    def publish(self, topic, message, qos=None, retain=False):
        if qos is None:
            qos = self.qos
        self.protocol.publish(topic, message, qos, retain)

    def subscribe(self):
        subscribers = list()

        # TODO:Subscribe to 2+ topics does not work

        for topic in self.subscribeTopics:
            d = self.protocol.subscribe(topic, 2)
            d.addCallbacks(MQTTMinidoBaseService._logGrantedQoS, MQTTMinidoBaseService._logFailure)
            subscribers.append(d)
            print("subscribing to {topic}".format(topic=topic))

        dlist = DeferredList(subscribers, consumeErrors=True)
        dlist.addCallback(MQTTMinidoBaseService._logAll)
        return dlist

    def _logFailure(failure):
        print("reported {message}", message=failure.getErrorMessage())
        return failure

    def _logGrantedQoS(value):
        return True

    def _logAll(*args):
        print("subscribed to topic.")


class MQTTBridgeServiceOptions(MQTTMinidoBaseServiceOptions):
    optParameters = [
        ["bridgeTopic", None, "low", "MQTT topic element for bridge to minido bus message"],
        ["readTopic", None, "read", "MQTT topic name sufix for messages received from minido bus"],
        ["writeTopic", None, "write", "MQTT topic name sufix for messages to be sent to minido bus"]
    ]


class MQTTBridgeService(MQTTMinidoBaseService):
    def __init__(self, config):
        MQTTMinidoBaseService.__init__(self, config)
        self.topicMinido = config["mqttHomeId"] + "/" + config["mqttTopic"] + "/"
        self.topicLow = self.topicMinido + config["bridgeTopic"] + "/"
        self.topicLowRead = self.topicLow + config["readTopic"]
        self.topicLowWrite = self.topicLow + config["writeTopic"]

#TODO: This class helps handling delegate messaging, it shall be replaced by Deffered or tasks in Refactor or callback
class BridgeHandler:
    def __init__(self, verbose=False):
        self.onReceivedDelegate = None
        self.verbose = verbose

    def receievedMessage(self, message):
        if self.onReceivedDelegate:
            if(self.verbose):
                self.printMessage(message)
            self.onReceivedDelegate.receievedMessage(message)
        else:
            self.printMessage(message)

    def sendMessage(self, message):
        pass

    def printMessage(self, message):
        chardata = ''.join(map(lambda i: '{:c}'.format(i), message))
        print(str(datetime.datetime.now()) + ': HANDLING : %s' % strHex(chardata))


class BridgeDelegate:
    def __init__(self, service):
        self.service = service

    def receievedMessage(self, message):
        self.service.sendMessage(message)
