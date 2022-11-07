#!/usr/bin/env python
import datetime

from minidopackage import MINIDO, EndPoint, STATUS


class MinidoState():
    def __init__(self, value = None):
        self.value : int = value
        self.lastUpdate = datetime.datetime.now()
        self.lastChange = self.lastUpdate


class MinidoModel():
    def __init__(self):
        self.endpoints = {}
        self.configs = {}
        self.defaults = {}
        self.onUpdatedEndpoitValue = None
        self.onUpdatedEndpoitConfig = None

        for x in MINIDO:
            self.updateEndpointValue(EndPoint(x), STATUS.OFF.value)

    def updateEndpointValue(self, endpoint, value, trigerUpdate=True):
        s = str(endpoint)
        prev_state = self.endpoints.setdefault(s, MinidoState())
        new_state = MinidoState(value)
        self.endpoints[s] = new_state

        if prev_state.value != value:
            if trigerUpdate:
                self.updatedEndpointValue(endpoint, value, prev_state.value, self.getEndpointFullConfig(endpoint), new_state.lastUpdate - prev_state.lastChange)
        else:
            self.endpoints[s].lastChange = prev_state.lastChange

    def getEndpointValue(self, endpoint):
        return self.getEndpointMinidoState(endpoint).value

    def getEndpointMinidoState(self, endpoint):
        sendpoint = str(endpoint)
        return self.endpoints.setdefault(sendpoint, MinidoState())

    def getEndpointsValues(self, endpoint):
        if(endpoint.isLeaf()):
            return [self.getEndpointValue(endpoint)]
        else:
            return [self.getEndpointValue(EndPoint(endpoint.minido, x + 1)) for x in range(8)]

    @classmethod
    def mergeConfigs(cls, *dicts):
        result = {}
        for d in dicts:
            result =  MinidoModel.__merge2Dict(result, d)

        return result

    @classmethod
    def __merge2Dict(cls, dict1, dict2):
        ''' Merge dictionaries and keep values of common keys in list'''
        dict3 = dict1 | dict2
        for key, value in dict3.items():
            if key in dict1 and key in dict2 and isinstance(value, dict):
                dict3[key] = MinidoModel.__merge2Dict(value,  dict1[key])
        return dict3

    def getEndpointFullConfig(self, endpoint):
        if endpoint is not None and endpoint.isLeaf():
            return MinidoModel.mergeConfigs(self.defaults.setdefault(str(None), {}),
                                            self.defaults.setdefault(endpoint.minido.name[:3], {}),
                                            self.defaults.setdefault(str(EndPoint(endpoint.minido)), {}),
                                            self.configs.setdefault(str(None), {}),
                                            self.configs.setdefault(endpoint.minido.name[:3], {}),
                                            self.configs.setdefault(str(EndPoint(endpoint.minido)), {}),
                                            self.configs.setdefault(str(endpoint), {}))
        else:
            return MinidoModel.mergeConfigs(self.defaults.setdefault(str(None), {}),
                                            self.defaults.setdefault(str(endpoint), {}),
                                            self.configs.setdefault(str(None), {}),
                                            self.configs.setdefault(str(endpoint), {}))



    def updateEndpointConfig(self, endpoint, config, trigerUpdate=True):
        prev = self.configs.setdefault(str(endpoint), {})
        self.configs[str(endpoint)] = config
        if trigerUpdate:
            self.updatedEndpointConfig(endpoint, None, config, prev, config)

    def setDefaultEndpointConfig(self, endpoint, config):
        self.defaults[str(endpoint)] = config

    def getEndpointConfigItem(self, endpoint, key):
        key = str(key)
        config = self.configs.setdefault(str(endpoint), {})
        return config.setdefault(key, None)

    def updateEndpointConfigItem(self, endpoint, key, value, trigerUpdate=True):
        key = str(key)
        config = self.configs.setdefault(str(endpoint), {})
        prev = config.setdefault(key, None)
        config[key] = value
        if trigerUpdate and prev != value:
            self.updatedEndpointConfig(endpoint, key, value, prev, config)

    def updatedEndpointValue(self, endpoint, value, prev, config, duration):
        if self.onUpdatedEndpoitValue:
            self.onUpdatedEndpoitValue(endpoint, value, prev, config, duration)

    def updatedEndpointConfig(self, endpoint, key, value, prev, config):
        if self.onUpdatedEndpoitConfig:
            self.onUpdatedEndpoitConfig(endpoint, key, value, prev, config)

