import datetime

from twisted.internet import reactor

from minidopackage import EndPoint, STATUS, MINIDO, CMD


class MinidoStrategy:
    def __init__(self, model):
        self.model = model
        self.model.updateEndpointValue(None, STATUS.OFF.value)

    def updateAvalability(self, packet):
        #model.updateEndpointValue(EndPoint(packet.src), STATUS.ON.value)
        pass


class D2000Strategy(MinidoStrategy):

    TEMPVAL = 128
    RESPONCE = 0.2
    RESPONCELINK = 0.8

    def __init__(self, model):
        MinidoStrategy.__init__(self, model)
        self.model.updateEndpointValue(None, STATUS.ON.value)

    def updateAvalability(self, packet):

        self.watchdogLink()
        #self.watchdogMinidoUnit(packet)



    def watchdogLink(self):
        self.model.updateEndpointValue(None, STATUS.ON.value)
        reactor.callLater(self.RESPONCELINK, self.checkLinkOffLine)

    def watchdogMinidoUnit(self, packet):
        ep = EndPoint(packet.src)
        value = self.model.getEndpointValue(ep)
        self.model.updateEndpointValue(ep, STATUS.ON.value, value == STATUS.OFF.value)
        if packet.src == MINIDO.D2000 and packet.isCommand() and packet.command == CMD.BUS_TOKEN_GRANT:
            ep = EndPoint(packet.dst)
            self.model.updateEndpointValue(ep, self.TEMPVAL, False)
            reactor.callLater(self.RESPONCE, self.checkMinidoUnitOffLine, ep)

    def checkMinidoUnitOffLine(self, ep):
        value = self.model.getEndpointValue(ep)
        if value != STATUS.ON.value:
            self.model.updateEndpointValue(ep, STATUS.OFF.value, value != self.TEMPVAL)

    def checkLinkOffLine(self):
        lastUpdate = self.model.endpoints[str(None)].lastUpdate
        minLastUpdate = datetime.datetime.now() - datetime.timedelta(seconds=self.RESPONCELINK)
        if lastUpdate <=  minLastUpdate:
            self.model.updateEndpointValue(None, STATUS.OFF.value)