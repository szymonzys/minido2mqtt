import json
from string import Template

from twisted.internet import reactor

from minidomodel import MinidoModel
from minidopackage import STATUS, MINIDO, ExiStatusPdu, ExoUpdatePdu, EndPoint
from mqtthomediscovery import MinidoHomeDiscoverable, DISCOVERY
from mqtthomeconfig import CONFIG, CONFIGTYPE, TOPICTYPE, DATAPOINT, COMMAND, PRESS, CONFIGDISCOVERYMODE, \
    CONFIGDEVICEDISCOVERYMODE, COVER
from mqtthomestrategy import MinidoStrategy, D2000Strategy


class DeviceCommand():
    def __init__(self, valueParseFunction, actionFunction):
        self.valueParseFunction = valueParseFunction
        self.actionFunction = actionFunction

class MinidoHomeDevice(MinidoHomeDiscoverable):

    __exceptions = []

    def __init__(self, protocol, datapoint = None):
        self.commands = {}
        self.protocol = protocol
        self.handeled_datapoints = [None, datapoint]
        self.ignored_datapoints = []
        self.autoConfig = True
        self.strategy = MinidoStrategy(self.protocol.model)
        self.commands[COMMAND.DISCOVER] = DeviceCommand(self.discoverMode, self.discoverEndPoints)
        self.commands[COMMAND.CONFIG_LOAD] = DeviceCommand(self.fileName, self.configLoad)
        self.commands[COMMAND.CONFIG_SAVE] = DeviceCommand(self.fileName, self.configSave)
        self.commands[COMMAND.CONFIG_SET] = DeviceCommand(lambda payload: json.loads(payload), self.configSet)
        self.commands[COMMAND.CONFIG_CLEAN] = DeviceCommand(lambda payload: None, self.configClean)

    # Low level handlers

    def isMyPdu(self, packet):
        return True

    def handleLowPdu(self, packet):
        if not isinstance(self.strategy, D2000Strategy) and packet.src == MINIDO.D2000:
            self.strategy = D2000Strategy(self.protocol.model)
        self.strategy.updateAvalability(packet)



    # Home and Model handlers

    def isMyEndpoint(self, endpoint):
        return endpoint is None or not (endpoint.isLeaf() or endpoint in MinidoHomeDevice.__exceptions)

    def handleModelStatusUpdate(self, endpoint, value, prev, config, duration):
        self.protocol.publishEndpoint(STATUS(value).name if value is not None else "", endpoint, TOPICTYPE.stat)

    def handleModelConfigUpdate(self, endpoint, key, value, prev, config):
        self.protocol.publishEndpoint(json.dumps(config, indent=4), endpoint, TOPICTYPE.config)

    def handleHomeStatusRestored(self, endpoint, payload, datapoint=None):
        if self.checkDatapoint(datapoint):
            self.handleDatapointHomeStatusRestore(endpoint, payload, datapoint)

    def checkDatapoint(self, datapoint):
        if datapoint in self.ignored_datapoints:
            return False
        elif datapoint in self.handeled_datapoints:
            return True
        else:
            raise ValueError("Incorrect status datapoint")

    def handleDatapointHomeStatusRestore(self, endpoint, payload, datapoint):
        self.protocol.model.updateEndpointValue(endpoint, STATUS[payload.decode("utf-8")].value, False)

    def handleHomeConfigRestored(self, endpoint, payload):
        if len(payload) == 0:
            self.protocol.model.updateEndpointConfig(endpoint, {}, False)
        else:
            self.protocol.model.updateEndpointConfig(endpoint, json.loads(payload), False)
            #if endpoint.minido.isExo() and endpoint.number > 10:
            #    self.protocol.model.updateEndpointConfigItem(
            #        EndPoint(endpoint.minido, int(endpoint.number // 10), CONFIG.cover, str(endpoint.number)), False)
            #    self.protocol.model.updateEndpointConfigItem(
            #        EndPoint(endpoint.minido, int(endpoint.number % 10), CONFIG.cover, str(endpoint.number)), False)

    def updateDiscovery(self, endpoint, discoverymode):
        if endpoint is not None and endpoint.isLeaf():
            self.publishDiscovery(endpoint, self.protocol.model.getEndpointFullConfig(endpoint), discoverymode)
        else:
            print("### DISCOVERY for childs of: " + str(endpoint))

            for str_endpoint in (self.protocol.model.endpoints | self.protocol.model.configs):
                s = str(endpoint)
                if (str_endpoint.startswith(s) or endpoint is None) and str_endpoint != s:
                    try:
                        point_endpoint = EndPoint.endpoint(str_endpoint)
                        self.publishDiscovery(point_endpoint, self.protocol.model.getEndpointFullConfig(point_endpoint),
                                            discoverymode)
                    except KeyError:
                        pass


    def publishDiscovery(self,   endpoint, config, discoverymode):
        if endpoint.isLeaf():
            discoverymode_ = (str(discoverymode) if discoverymode is not None else config[str(CONFIG.discoverymode)])
            if discoverymode_ == str(CONFIGDISCOVERYMODE.label) and str(CONFIG.label) not in config:
                return
            if discoverymode_ == str(CONFIGDISCOVERYMODE.none):
                return

            type_ = config[str(CONFIG.type)]
            if type_ == str(CONFIGTYPE.dimmer) and endpoint.number > 4:
                return

            config_type_ = config[str(CONFIG.typediscovery)][type_]
            component = config_type_[str(CONFIG.type)]
            discovery = MinidoModel.mergeConfigs(config[str(CONFIG.discovery)], config_type_[str(CONFIG.discovery)])
            discovery[str(DISCOVERY.name)] = config.setdefault(str(CONFIG.label), str(endpoint))

            devicediscoverymode_ = config[str(CONFIG.devicediscoverymode)]
            if devicediscoverymode_ == str(CONFIGDEVICEDISCOVERYMODE.none):
                del discovery[str(DISCOVERY.device)]
            elif devicediscoverymode_ == str(CONFIGDEVICEDISCOVERYMODE.virtual):
                if str(CONFIG.location) in config:
                    discovery[str(DISCOVERY.device)] = MinidoHomeDiscoverable.virtualDevice(config[str(CONFIG.location)])
                else:
                    del discovery[str(DISCOVERY.device)]

            t = Template(json.dumps(discovery, indent=4))
            message = t.safe_substitute(endpoint=str(endpoint), minido=str(endpoint.minido.name))
            #print("### DISCOVERY : " + component)
            self.protocol.publishDiscovery(endpoint, component, message)
            print("### DISCOVERY : " + component + ", payload : " + message)



    # Handle Commands

    def handleHomeCommand(self, endpoint, payload, command):
        devcmnd = self.commands[command]
        devcmnd.actionFunction(endpoint, devcmnd.valueParseFunction(payload))


    def discoverMode(self, payload):
        if len(payload) > 0:
            return CONFIGDISCOVERYMODE[payload.decode("utf-8")]
        else:
            return None

    def discoverEndPoints(self, endpoint, value):
        print(":::DISCOVERY COMMAND::: " + str(endpoint))
        if value is not None:
            discoverymode = value
            print("  Mode: " + str(discoverymode))
        self.updateDiscovery(endpoint, value)

    def fileName(self, payload):
        return payload.decode("utf-8")

    def configClean(self, endpoint, value):
        if endpoint is None:
            print(":::CLEAN CONFIG COMMAND::: ")
            self.__configClean()

    def __configClean(self):
        for str_endpoint in self.protocol.model.configs:
            self.protocol.publishEndpoint(None, str_endpoint if str_endpoint != "None" else None,
                                          TOPICTYPE.config)

    def configLoad(self, endpoint, value):
        if endpoint is None:
            print(":::LOAD CONFIG COMMAND::: " + value)
            with open(value, 'r') as fp:
                self.__configClean()
                self.protocol.model.configs = json.load(fp)
                self.__configSet()

    def __configSet(self):
        for str_endpoint in self.protocol.model.configs:
            self.protocol.publishEndpoint(json.dumps(self.protocol.model.configs[str_endpoint], indent=4),
                                          str_endpoint if str_endpoint != "None" else None, TOPICTYPE.config)

    def configSave(self, endpoint, value):
        if endpoint is None:
            print(":::SAVE CONFIG COMMAND::: " + value)
            with open(value, 'w') as fp:
                for key in list(self.protocol.model.configs):
                    if len(self.protocol.model.configs[key]) == 0:
                        del self.protocol.model.configs[key]
                json.dump(self.protocol.model.configs, fp, indent=4)

    def configSet(self, endpoint, value):
        if endpoint is None:
            print(":::SET CONFIG COMMAND::: ")
            self.__configClean()
            self.protocol.model.configs = value
            self.__configSet()

    # Helpers

    def autoconfigMinidoType(self, endpoint, minidoType):
        minido = endpoint.minido
        self.protocol.model.updateEndpointConfigItem(EndPoint(minido), CONFIG.type, minidoType.name)
        print(":::AUTOCONFIG::: {minido} tagged as {minidotype}".format(minido=minido.name,
                                                                        minidotype=minidoType.name))


class ExoDevice(MinidoHomeDevice):
    def __init__(self, protocol):
        MinidoHomeDevice.__init__(self, protocol, DATAPOINT.POWER)
        self.ignored_datapoints.append(DATAPOINT.BRIGHTNESS)
        self.ignored_datapoints.append(DATAPOINT.COVER)
        self.handeled_datapoints.append(DATAPOINT.POSITION)
        self.commands[COMMAND.POWER] = DeviceCommand(lambda payload: STATUS[payload.decode("utf-8")].value,
                                                     self.sendAgregatedExoPachage)
        self.commands[COMMAND.BRIGHTNESS] = DeviceCommand(self.valueBrightness,
                                                          self.sendAgregatedExoPachage)
        self.commands[COMMAND.COVER] = DeviceCommand(lambda payload: COVER[payload.decode("utf-8")],
                                                     self.sendCoverControl)
        self.commands[COMMAND.POSITION] = DeviceCommand(lambda payload: int(payload.decode("utf-8")),
                                                     self.sendCoverSetPosition)
    # Low level handlers

    def isMyPdu(self, packet):
        return isinstance(packet, ExoUpdatePdu)

    def handleLowPdu(self, packet):
        packet = ExoUpdatePdu(packet.chardata)
        params = packet.params
        for x in range(8):
            self.protocol.model.updateEndpointValue(packet.endpoint(x), params[x])

    # Home and Model handlers

    def isMyEndpoint(self, endpoint):
        return endpoint is not None and endpoint.isLeaf() and endpoint.minido.isExo()

    def handleDatapointHomeStatusRestore(self, endpoint, payload, datapoint):
        if datapoint == DATAPOINT.POSITION:
           self.protocol.model.updateEndpointValue(endpoint, int(payload.decode("utf-8")), False)
        else:
            MinidoHomeDevice.handleDatapointHomeStatusRestore(self, endpoint, payload, datapoint)



    def handleModelStatusUpdate(self, endpoint, value, prev, config, duration):
        if(value == 0):
            message = STATUS.OFF.name
        else:
            message = STATUS.ON.name

        # check if marked as cover
        isCover = config.setdefault(str(CONFIG.type), None) == CONFIGTYPE.cover.name
        isCoverItem = str(CONFIG.cover) in config
        #check if marked as dimmer
        isDimmer = config.setdefault(str(CONFIG.type), None) == CONFIGTYPE.dimmer.name
        isDimerValue = not (value == 0 or value == 0xFF)
        isPulse = value == STATUS.Pulse.value


        #autodetect dimmer
        if not isDimmer and isDimerValue and str(CONFIG.type) not in config:
            if self.protocol.autoConfig:
                self.autoconfigMinidoType(endpoint, CONFIGTYPE.dimmer)
                isDimmer = True
            else:
                print(":::AUTOCONFIG::: Ignored: Dimer tagging")

        # handle dimmer change
        if isDimmer:
            self._handleDimerStatusUpdate(endpoint, isDimerValue, isPulse, value)

        # handle cover item change
        if isCoverItem:
            self._handleCoverItemStatusUpdate(config, endpoint, value, duration)

        if isCover:
            self._handleCoverPositionUpdate(config, endpoint, value)
            return

        #publish state anyway
        self.protocol.publishEndpoint(message, endpoint, TOPICTYPE.stat, DATAPOINT.POWER)

    def _handleCoverPositionUpdate(self, config, endpoint, value):
        self.protocol.publishEndpoint(str(value), endpoint, TOPICTYPE.stat, DATAPOINT.POSITION)

    def _handleCoverItemStatusUpdate(self, config, endpoint, value, duration):
        cover_pair = config[str(CONFIG.cover)]
        cover_time = config[str(CONFIG.covertime)]
        cover_endpoint = EndPoint(endpoint.minido, int(cover_pair))
        cover_state = COVER(cover_pair.find(str(endpoint.number)))

        if value == STATUS.ON.value:
            self.protocol.publishEndpoint(str(cover_state),
                                          cover_endpoint, TOPICTYPE.stat, DATAPOINT.COVER)

        else:
            if self.protocol.model.getEndpointValue(
                    EndPoint(endpoint.minido, int(cover_pair.replace(str(endpoint.number),"")))) == STATUS.OFF.value:
                self.protocol.publishEndpoint(str(COVER.stopped), cover_endpoint, TOPICTYPE.stat, DATAPOINT.COVER)
            self._updatePosition(cover_endpoint, cover_state, cover_time, duration)

    def _updatePosition(self, cover_endpoint, cover_state, cover_time, duration):
        pos = self.protocol.model.getEndpointValue(cover_endpoint)
        pos = pos if pos is not None else 100

        pos = pos + ((-1 if cover_state == COVER.closing else 1) * 100 * duration.total_seconds() / cover_time)
        if pos >= 100:
            pos = 100
            self.protocol.publishEndpoint(str(COVER.open), cover_endpoint, TOPICTYPE.stat, DATAPOINT.COVER)
        elif pos <= 0:
            pos = 0
            self.protocol.publishEndpoint(str(COVER.closed), cover_endpoint, TOPICTYPE.stat, DATAPOINT.COVER)
        self.protocol.model.updateEndpointValue(cover_endpoint, int(pos))

    def _handleDimerStatusUpdate(self, endpoint, isDimerValue, isPulse, value):
        brigh = str(value)
        if (isPulse):
            # If in pulse mode clean brightness (do not know the actual brightness value)
            self.protocol.model.updateEndpointConfigItem(endpoint, CONFIG.brightness.name, None)
            brigh = ""
        elif isDimerValue:
            self.protocol.model.updateEndpointConfigItem(endpoint, CONFIG.brightness.name, value)
        if isDimerValue:
            self.protocol.publishEndpoint(brigh, endpoint, TOPICTYPE.stat, DATAPOINT.BRIGHTNESS)



    # Commands helpers

    def valueBrightness(self, payload):
        value = int(payload.decode("utf-8"))
        value = (value // 2) << 1  # round to even
        if value < 0:
            value = 0
        elif value > 100:
            value = 100
        return value

    def sendAgregatedExoPachage(self, endpoint, value):
        minido = endpoint.minido
        values = self.protocol.model.getEndpointsValues(EndPoint(minido))
        values[endpoint.number - 1] = value
        self._sendExoPackage(minido, values)

    def _sendExoPackage(self, minido, values):
        pdu = ExoUpdatePdu()
        pdu.src = MINIDO.PC
        pdu.dst = minido
        allset = pdu.copy2payload(values, 8, 1)
        if allset:
            self.protocol.service.sendPackage(pdu)
        else:
            print("ERROR not enough data to execute COMMAND")

    def sendCoverControl(self, endpoint, value):
        minido = endpoint.minido
        exo_values = self.protocol.model.getEndpointsValues(EndPoint(minido))
        match value:
            case COVER.open:
                exo_values[endpoint.number // 10 - 1] = STATUS.ON.value
                exo_values[endpoint.number % 10 - 1] = STATUS.OFF.value
                # Time to stop
                move_endpoint = EndPoint(endpoint.minido, endpoint.number // 10)
                config = self.protocol.model.getEndpointFullConfig(move_endpoint)
                cover_time = config[str(CONFIG.covertime)]
                pass
            case COVER.close:
                exo_values[endpoint.number // 10 - 1] = STATUS.OFF.value
                exo_values[endpoint.number % 10 - 1] = STATUS.ON.value
                # Time to stop
                move_endpoint = EndPoint(endpoint.minido, endpoint.number % 10)
                config = self.protocol.model.getEndpointFullConfig(move_endpoint)
                cover_time = config[str(CONFIG.covertime)]
                pass
            case COVER.stop:
                exo_values[endpoint.number // 10 - 1] = STATUS.OFF.value
                exo_values[endpoint.number % 10 - 1] = STATUS.OFF.value
                cover_time = 0
                pass
        self._sendExoPackage(minido, exo_values)
        if cover_time > 0:
            reactor.callLater(cover_time, self.sendCoverControl, endpoint, COVER.stop)

    def sendCoverSetPosition(self, endpoint, value):
        pos = self.protocol.model.getEndpointValue(endpoint)
        delta = pos - value
        move_endpoint_number = (endpoint.number // 10) if delta < 0 else (endpoint.number % 10)

        if delta != 0:
            move_endpoint = EndPoint(endpoint.minido, move_endpoint_number)
            config = self.protocol.model.getEndpointFullConfig(move_endpoint)
            cover_time = config[str(CONFIG.covertime)]
            self.sendAgregatedExoPachage(move_endpoint, STATUS.ON.value)
            reactor.callLater(cover_time * abs(delta) / 100, self.sendAgregatedExoPachage, move_endpoint, STATUS.OFF.value)


class ExiDevice(MinidoHomeDevice):
    def __init__(self, protocol):
        MinidoHomeDevice.__init__(self, protocol, DATAPOINT.BUTTON)
        self.ignored_datapoints.append(DATAPOINT.TEMPERATURE)
        self.commands[COMMAND.BUTTON] = DeviceCommand(lambda payload: STATUS[payload.decode("utf-8")].value,
                                                      self.sendAgregatedExiPackage)
        self.commands[COMMAND.PRESS] = DeviceCommand(self.valuePress, self.sendOnOffExiPackage)

    # Low level handlers

    def isMyPdu(self, packet):
        return isinstance(packet, ExiStatusPdu)

    def handleLowPdu(self, packet):
        self.protocol.model.updateEndpointValue(packet.endpoint, packet.valueInt)

    # Home and Model handlers

    def isMyEndpoint(self, endpoint):
        return endpoint is not None and endpoint.isLeaf() and endpoint.minido.isExi()

    def handleModelStatusUpdate(self, endpoint, value, prev, config, duration):
        if config.setdefault(str(CONFIG.type), None) == CONFIGTYPE.temperature.name:
            # publish temperature instead of status for tagged EXIs
            self.protocol.publishEndpoint(str(0.5 * value), endpoint, TOPICTYPE.stat, DATAPOINT.TEMPERATURE)
        elif self.autoConfig and not STATUS.isValueIn(value):
            # if autoconfig and temperature detected, update config tag, and publish temperature
            self.autoconfigMinidoType(endpoint, CONFIGTYPE.temperature)
            self.protocol.publishEndpoint(str(0.5 * value), endpoint, TOPICTYPE.stat, DATAPOINT.TEMPERATURE)
        elif STATUS.isValueIn(value):
            # Report button state
            self.protocol.publishEndpoint(STATUS(value).name, endpoint, TOPICTYPE.stat, DATAPOINT.BUTTON)

    # Commands helpers

    def valuePress(self, payload):
        try:
            return PRESS[payload.decode("utf-8")].value
        except :
            return float(payload.decode("utf-8"))

    def sendOnOffExiPackage(self, endpoint, value):
        self.sendAgregatedExiPackage(endpoint, STATUS.ON.value)
        reactor.callLater(value, self.sendAgregatedExiPackage, endpoint, STATUS.OFF.value)

    def sendAgregatedExiPackage(self, endpoint, value):
        pdu = ExiStatusPdu()
        pdu.src = endpoint.minido
        pdu.dst = MINIDO.D2000
        pdu.endpoint = endpoint
        pdu.endpointValue = value
        self.protocol.service.sendPackage(pdu)


