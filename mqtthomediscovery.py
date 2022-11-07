from aenum import Enum, auto

from minidopackage import STATUS
from mqtthomeconfig import CONFIG, CONFIGTYPE, TOPICTYPE, DATAPOINT, COMMAND, PRESS, CONFIGDISCOVERYMODE, \
    CONFIGDEVICEDISCOVERYMODE, COVER


class MinidoHomeDiscoverable:
    @classmethod
    def initModel(cls, model, topic):
        model.setDefaultEndpointConfig(None,
                                    {
                                        str(CONFIG.type): str(CONFIGTYPE.switch),
                                        str(CONFIG.discoverymode): str(CONFIGDISCOVERYMODE.label),
                                        str(CONFIG.devicediscoverymode): str(CONFIGDEVICEDISCOVERYMODE.minido),
                                        str(CONFIG.typediscovery): {
                                            str(CONFIGTYPE.switch): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.switch),
                                                str(CONFIG.discovery): {
                                                }
                                            }
                                        },
                                        str(CONFIG.discovery): {
                                            "~": topic[:-1],
                                            str(DISCOVERY.unique_id): "${endpoint}",
                                            str(DISCOVERY.object_id): "${endpoint}",
                                            str(DISCOVERY.device): {
                                                str(DISCOVERYDEVICE.manufacturer): "AnB S.A.",
                                                str(DISCOVERYDEVICE.identifiers): ["MINIDO:${minido}"],
                                                str(DISCOVERYDEVICE.name): "MINIDO ${minido}"
                                            }
                                        }
                                    })
        model.setDefaultEndpointConfig("EXI",
                                    {
                                        #str(CONFIG.component): str(CONFIGCOMPONENT.button),
                                        str(CONFIG.typediscovery): {
                                            str(CONFIGTYPE.button_short): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.button),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.command_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.cmnd) + "/" + str(COMMAND.PRESS),
                                                    str(DISCOVERY.payload_press): str(PRESS.short)
                                                }
                                            },
                                            str(CONFIGTYPE.button_long): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.button),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.command_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.cmnd) + "/" + str(COMMAND.PRESS),
                                                    str(DISCOVERY.payload_press): str(PRESS.long)
                                                }
                                            },
                                            str(CONFIGTYPE.switch): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.switch),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.BUTTON),
                                                    str(DISCOVERY.command_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.cmnd) + "/" + str(COMMAND.BUTTON)

                                                }
                                            },
                                            str(CONFIGTYPE.temperature): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.sensor),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.TEMPERATURE),
                                                    str(DISCOVERY.device_class): str(DISCOVERYDEVICECLASS.temperature),
                                                    str(DISCOVERY.unit_of_measurement): "°C"
                                                }
                                            },
                                            str(CONFIGTYPE.light_sensor): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.binary_sensor),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.BUTTON),
                                                    str(DISCOVERY.device_class): str(DISCOVERYDEVICECLASS.light),
                                                    str(DISCOVERY.payload_off): STATUS.ON.name,
                                                    str(DISCOVERY.payload_on): STATUS.OFF.name
                                                }
                                            },
                                            str(CONFIGTYPE.motion_sensor): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.binary_sensor),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.BUTTON),
                                                    str(DISCOVERY.device_class): str(DISCOVERYDEVICECLASS.motion)
                                                }
                                            },
                                            str(CONFIGTYPE.binary_sensor): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.binary_sensor),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.BUTTON)
                                                }
                                            }
                                        },
                                        str(CONFIG.discovery): {
                                            str(DISCOVERY.device): {
                                                str(DISCOVERYDEVICE.model): str(DISCOVERYDEVICEMODEL.EXIBUS)
                                            }
                                        }
                                    })
        model.setDefaultEndpointConfig("EXO",
                                    {
                                        #str(CONFIG.component): str(CONFIGCOMPONENT.light),
                                        str(CONFIG.typediscovery): {
                                            str(CONFIGTYPE.dimmer): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.light),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.brightness_state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.BRIGHTNESS),
                                                    str(DISCOVERY.brightness_command_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.cmnd) + "/" + str(COMMAND.BRIGHTNESS),
                                                    str(DISCOVERY.brightness_scale): 100,
                                                    str(DISCOVERY.device): {
                                                        str(DISCOVERYDEVICE.model): str(DISCOVERYDEVICEMODEL.EXO_DIM)
                                                    }
                                                }
                                            },
                                            str(CONFIGTYPE.cover): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.cover),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.COVER),
                                                    str(DISCOVERY.command_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.cmnd) + "/" + str(COMMAND.COVER),
                                                    str(DISCOVERY.position_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.stat) + "/" + str(DATAPOINT.POSITION),
                                                    str(DISCOVERY.set_position_topic): "~/${endpoint}/" + str(
                                                        TOPICTYPE.cmnd) + "/" + str(DATAPOINT.POSITION),
                                                    str(DISCOVERY.payload_open): str(COVER.open),
                                                    str(DISCOVERY.payload_close): str(COVER.close),
                                                    str(DISCOVERY.payload_stop): str(COVER.stop),
                                                    str(DISCOVERY.state_open): str(COVER.open),
                                                    str(DISCOVERY.state_closed): str(COVER.closed),
                                                    str(DISCOVERY.state_opening): str(COVER.opening),
                                                    str(DISCOVERY.state_closing): str(COVER.closing),
                                                    str(DISCOVERY.state_stopped): str(COVER.stopped),
                                                    str(DISCOVERY.position_closed): 0,
                                                    str(DISCOVERY.position_open): 100,
                                                    str(DISCOVERY.device_class): str(DISCOVERYDEVICECLASS.shutter)
                                                }
                                            },
                                            str(CONFIGTYPE.switch): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.switch),
                                                str(CONFIG.discovery): {
                                                    str(DISCOVERY.device_class): str(DISCOVERYDEVICECLASS.outlet)
                                                }
                                            },
                                            str(CONFIGTYPE.light): {
                                                str(CONFIG.type): str(DISCOVERYCOMPONENT.light),
                                                str(CONFIG.discovery): {

                                                }
                                            }
                                        },
                                        str(CONFIG.discovery): {
                                            str(DISCOVERY.state_topic): "~/${endpoint}/" + str(
                                                TOPICTYPE.stat) + "/" + str(DATAPOINT.POWER),
                                            str(DISCOVERY.command_topic): "~/${endpoint}/" + str(
                                                TOPICTYPE.cmnd) + "/" + str(COMMAND.POWER),
                                            str(DISCOVERY.device): {
                                                str(DISCOVERYDEVICE.model): str(DISCOVERYDEVICEMODEL.EXO8)
                                            }
                                        }
                                    })

    @classmethod
    def virtualDevice(cls, location):
        return {
            str(DISCOVERYDEVICE.manufacturer): "Minido MQTT Bridge",
            str(DISCOVERYDEVICE.identifiers): [location],
            str(DISCOVERYDEVICE.name): "Virtual Minido Device (" + location + ")",
            str(DISCOVERYDEVICE.suggested_area): location
        }

class DISCOVERYCOMPONENT(Enum):
    switch = auto()
    binary_sensor = auto()
    button = auto()
    light = auto()
    sensor = auto()
    cover = auto()
    def __str__(self):
        return self.name


class DISCOVERY(Enum):
    #generic
    availability_topic = auto()
    state_topic = auto()
    command_topic = auto()
    device = auto()
    device_class = auto()
    name = auto()
    object_id = auto()
    unique_id = auto()

    #binary_sensor
    payload_off  = auto()
    payload_on  = auto()

    #Light
    brightness_command_topic = auto()
    brightness_state_topic = auto()
    brightness_scale = auto()

    #cover
    position_topic = auto()
    set_position_topic = auto()
    payload_open = auto()
    payload_close = auto()
    payload_stop = auto()
    state_opening = auto()
    state_closing = auto()
    state_stopped = auto()
    state_open = auto()
    state_closed = auto()
    position_closed = auto()
    position_open = auto()
    #Sensor
    unit_of_measurement = auto()

    #Button
    payload_press = auto()

    def __str__(self):
        return self.name


class DISCOVERYDEVICECLASS(Enum):
    outlet = auto()
    temperature = auto()
    motion = auto()
    light = auto()
    shutter = auto()
    def __str__(self):
        return self.name


class DISCOVERYDEVICE(Enum):
    manufacturer  = auto()
    model = auto()
    name = auto()
    identifiers = auto()
    suggested_area = auto()

    def __str__(self):
        return self.name


class DISCOVERYDEVICEMODEL(Enum):
    EXIBUS = "EXIBUS"
    EXO_DIM = "EXO-DIM"
    EXO8 = "EXO8"
    EXO8_220 = "EXO8-220"
    EXO8_DOMO = "EXO8-DOMO"

    def __str__(self):
        return self.value


