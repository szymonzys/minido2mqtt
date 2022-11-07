#!/usr/bin/env python
import json

from aenum import Enum, auto

from minidopackage import EndPoint
from mqtthomedevice import MinidoHomeDevice, ExiDevice, ExoDevice
from mqtthomediscovery import TOPICTYPE, DATAPOINT, COMMAND

"""
    MQTT protocol (home level) for generic home automation integration (OpenHAB or Home Assistant).
    MQTT messaging structure is as follows
    
    Generic:
    {myhome}/{minido}/{home}/config <=> JSON dict() 
    {myhome}/{minido}/{home}/[[D2000|PC|EX[O|I]xx]/config <=> JSON dict()
    {myhome}/{minido}/{home}/[[D2000|PC|EX[O|I]xx]/stat => ON 
    {myhome}/{minido}/{home}/EX[O|I]xx-x[x]/config <=> JSON dict()
    {myhome}/{minido}/{home}/cmnd/CONFIG_SAVE <= filename.ext
    {myhome}/{minido}/{home}/cmnd/CONFIG_LOAD <= filename.ext
    {myhome}/{minido}/{home}/cmnd/DISCOVER <= ""|all|label
    {myhome}/{minido}/{home}/[[D2000|PC|EX[O|I]xx]/cmnd/DISCOVER <= ""|all|label
    {myhome}/{minido}/{home}/EX[O|I]xx-x[x]/cmnd/DISCOVER <= ""|all|label
    
    EXI:
    {myhome}/{minido}/{home}/EXOxx-x[x]/stat/TEMPERATURE => -64, 64 (in celsius)
    {myhome}/{minido}/{home}/EXIxx-x[x]/stat/BUTTON => ON/OFF
    {myhome}/{minido}/{home}/EXOxx-x[x]/cmnd/BUTTON <= ON/OFF
    {myhome}/{minido}/{home}/EXIxx-x[x]/cmnd/PRESS <= long/short/{float} - time in seconds for pressing the button
    
    EXO:
    {myhome}/{minido}/{home}/EXOxx-x/stat/POWER => ON/OFF
    {myhome}/{minido}/{home}/EXOxx-x/cmnd/POWER <= ON/OFF
    {myhome}/{minido}/{home}/EXOxx-xy/stat/COVER => open, opening, closing, closed, stopped
    {myhome}/{minido}/{home}/EXOxx-xy/cmnd/COVER <= open, close, stop
    {myhome}/{minido}/{home}/EXOxx-xy/stat/POSITION => 0-100
    {myhome}/{minido}/{home}/EXOxx-xy/cmnd/POSITION <= 0-100
    {myhome}/{minido}/{home}/EXOxx-x/stat/BRIGHTNESS => 0-100 (% 0 is smallest and increase by 2 up to 100)
    {myhome}/{minido}/{home}/EXOxx-x/cmnd/BRIGHTNESS <= 0-100 (% 0 is smallest and increase by 2 up to 100), > 100 is considered 100, bellow 0 is cosidered 0
    
    Please note: only /cmnd are actually sent to MINIDO.
    If you update /stat it is like update of the database cache
    Sequence of flow is as followes:
    status: MINIDO => ../low => MODEL => ../home => MODEL
    cmnd: ../home => ../low => MODEL => ../home => MODEL  
    config: MODEL => ../home => MODEL  
    
    
    For coders: configs are inherited from home, to Exi/Exo node down to endpoint. 
    
    TODO List:
    4) Improve error handling for wrong topics or parameters parsing
    
"""
class MQTTHomeProtocol():
    def __init__(self, service):
        self.service = service
        self.model = service.model
        self.devices = service.devices
        #Set default config
        MinidoHomeDevice.initModel(self.model, self.service.topicHome)

        # auto configuration based on package values inspection
        self.autoConfig = False

        #Set callbacks to model update
        self.model.onUpdatedEndpoitValue = self.onUpdatedEndpoitValue
        self.model.onUpdatedEndpoitConfig = self.onUpdatedEndpoitConfig



    def onUpdatedEndpoitValue(self, endpoint, value, prev, config, duration):
        for dev in self.devices:
            if dev.isMyEndpoint(endpoint):
                dev.handleModelStatusUpdate(endpoint, value, prev, config, duration)

    def onUpdatedEndpoitConfig(self, endpoint, key, value, prev, config):
        for dev in self.devices:
            if dev.isMyEndpoint(endpoint):
                dev.handleModelConfigUpdate(endpoint, key, value, prev, config)

    def homeLevelMessageReceived(self, topic, payload):
        str_endpoint, endpoint = self._endpointFromTopic(topic)
        sufixIndex = topic.rfind("/")
        topicSufix = topic[sufixIndex + 1:]
        topicPreSufix = topic[topic[:sufixIndex].rfind("/") + 1:sufixIndex]
        topictype = topicSufix

        try:
            for dev in self.devices:
                if dev.isMyEndpoint(endpoint):
                    if topicSufix == TOPICTYPE.config.name:
                        self._printReceived(str_endpoint, payload, TOPICTYPE[topictype])
                        dev.handleHomeConfigRestored(str_endpoint, payload)
                    elif topicSufix == TOPICTYPE.stat.name:
                        pass
                    else:
                        topictype = topicPreSufix
                        if topicPreSufix == TOPICTYPE.stat.name:
                            # self.printReceived(endpoint, payload, TOPICTYPE[topictype])
                            dev.handleHomeStatusRestored(endpoint, payload, DATAPOINT[topicSufix])
                        elif topicPreSufix == TOPICTYPE.cmnd.name:
                            self._printReceived(endpoint, payload, TOPICTYPE[topictype])
                            dev.handleHomeCommand(endpoint, payload, COMMAND[topicSufix])
        except (ValueError, IndexError):
            self._printReceived(endpoint, payload, TOPICTYPE[topictype], " INCORECT")

    def publish(self, topic, message, retain=True):
        self.service.publish(topic, message if message is not None else bytearray(), None, retain)


    def publishDiscovery(self, endpoint, component, message, retain=True):
        self.publish(self.service.topicDiscovery + component + "/" + str(endpoint) + "/config", message, retain)

    def publishEndpoint(self, message, endpoint, topicType, topicDatapoint = None, retain=True):
        topic = self._buildTopic(endpoint, topicType, topicDatapoint)
        self.publish(topic, message, retain)
        self._printPublished(message, topic)

    def cleanPublishedEndpoint(self, endpoint, topicType):
        topic = self._buildTopic(endpoint, topicType, None)
    # Helper methods bellow

    def _printReceived(self, endpoint, payload, topictype, extra =""):
        if self.service.verbose:
            print("@HOME: " + str(endpoint) + " RECIVED" + extra + ": " + str(topictype) + ", PAYLOAD: " + str(payload) )

    def _printPublished(self, message, topic):
        if self.service.verbose:
            print("@HOME: " + topic[len(self.service.topicHome):] + " PUBLISHED:" + str(message))

    def _buildTopic(self, endpoint, topicType, topicDatapoint = None):
        return "{homeTopic}{endPoint}{topicType}{topicDatapoint}".format(homeTopic=self.service.topicHome,
                                                                         endPoint=(str(endpoint) + "/")
                                                                         if endpoint is not None else "",
                                                                         topicType=str(topicType),
                                                                         topicDatapoint= ("/" + str(topicDatapoint))
                                                                         if topicDatapoint is not None else "")

    def _endpointFromTopic(self, topic):
        topic = topic[len(self.service.topicHome):]
        pos = topic.find("/")
        if pos == -1:
            return None, None
        else:
            topic = topic[:pos]
            try:
                return topic, EndPoint.endpoint(topic)
            except KeyError:
                pass
            return topic, None


