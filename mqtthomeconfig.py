from aenum import Enum, auto


class CONFIG(Enum):
    type = auto()
    label = auto()
    location = auto()
    typediscovery = auto()
    brightness = auto()
    discovery = auto()
    discoverymode = auto()
    devicediscoverymode = auto()
    cover = auto()
    covertime = auto()

class CONFIGTYPE(Enum):
    temperature = auto()
    dimmer = auto()
    switch = auto()
    binary_sensor = auto()
    motion_sensor = auto()
    light_sensor = auto()
    button_short = auto()
    button_long = auto()
    light = auto()
    cover = auto()
    def __str__(self):
        return self.name


class TOPICTYPE(Enum):
    stat = auto()
    cmnd = auto()
    config = auto()
    def __str__(self):
        return self.name


class DATAPOINT(Enum):
    POWER = auto()
    BRIGHTNESS = auto()
    BUTTON = auto()
    TEMPERATURE = auto()
    COVER = auto()
    POSITION = auto()
    def __str__(self):
        return self.name


class COMMAND(Enum):
    POWER = DATAPOINT.POWER
    BRIGHTNESS = DATAPOINT.BRIGHTNESS
    BUTTON = DATAPOINT.BUTTON
    PRESS = auto()
    COVER = DATAPOINT.COVER
    POSITION = DATAPOINT.POSITION
    DISCOVER = auto()
    CONFIG_SAVE = auto()
    CONFIG_LOAD = auto()
    CONFIG_SET = auto()
    CONFIG_CLEAN = auto()
    def __str__(self):
        return self.name


class PRESS(Enum):
    short = 0.4
    long = 3.0
    def __str__(self):
        return self.name

class COVER(Enum):
    opening = 0
    closing = 1
    stopped = 2
    closed = 4
    open = 10
    close = 11
    stop = 12
    def __str__(self):
        return self.name

class CONFIGDISCOVERYMODE(Enum):
    all = auto()
    label = auto()
    none = auto()
    def __str__(self):
        return self.name

class CONFIGDEVICEDISCOVERYMODE(Enum):
    minido = auto()
    virtual = auto()
    none = auto()
    def __str__(self):
        return self.name