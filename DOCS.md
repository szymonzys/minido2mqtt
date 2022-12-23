# Home Assistant Add-on: MINIDO2MQTT

This is Home Assistent addon for using AnB (Belgium) Minido or D2000 system within Home Assistent as MQTT devices. 

## MINIDO/D20000



## Services

It contains 2 microservices:

- **minido_link** is link between TCPCLient/Serial conectivity to MINIDO and MQTT. It directly transmits minido packages in its raw/binary format and place it into the MQTT topic. It constitutes **LOW protocol**.

- **minido_home** is bridge between LOW protocl and Home Assistant MQTT Item (https://www.home-assistant.io/integrations/mqtt/). It allowes for storing configurations for each MINIDO item. It supports Home Assistant discovery messages for configured items. It constitutes **HOME protocol**.



### LOW protocol interface is defined as follows:

- {myhome}/{minido}/{low}/{read} => Minido package in binary format

- {myhome}/{minido}/{low}/{write} <= Minido package in binary format


### HOME protocol interface is defined as follows:

Generic:

- {myhome}/{minido}/{home}/config <=> JSON dict() 

- {myhome}/{minido}/{home}/[[D2000|PC|EX[O|I]xx]/config <=> JSON dict()

- {myhome}/{minido}/{home}/[[D2000|PC|EX[O|I]xx]/stat => ON 

- {myhome}/{minido}/{home}/EX[O|I]xx-x[x]/config <=> JSON dict()

- {myhome}/{minido}/{home}/cmnd/CONFIG_SAVE <= filename.ext

- {myhome}/{minido}/{home}/cmnd/CONFIG_LOAD <= filename.ext

- {myhome}/{minido}/{home}/cmnd/DISCOVER <= ""|all|label

- {myhome}/{minido}/{home}/[[D2000|PC|EX[O|I]xx]/cmnd/DISCOVER <= ""|all|label

- {myhome}/{minido}/{home}/EX[O|I]xx-x[x]/cmnd/DISCOVER <= ""|all|label


EXI:

- {myhome}/{minido}/{home}/EXOxx-x[x]/stat/TEMPERATURE => -64, 64 (in celsius)

- {myhome}/{minido}/{home}/EXIxx-x[x]/stat/BUTTON => ON/OFF

- {myhome}/{minido}/{home}/EXOxx-x[x]/cmnd/BUTTON <= ON/OFF

- {myhome}/{minido}/{home}/EXIxx-x[x]/cmnd/PRESS <= long/short/{float} - time in seconds for pressing the button


EXO:

- {myhome}/{minido}/{home}/EXOxx-x/stat/POWER => ON/OFF

- {myhome}/{minido}/{home}/EXOxx-x/cmnd/POWER <= ON/OFF

- {myhome}/{minido}/{home}/EXOxx-xy/stat/COVER => open, opening, closing, closed, stopped

- {myhome}/{minido}/{home}/EXOxx-xy/cmnd/COVER <= open, close, stop

- {myhome}/{minido}/{home}/EXOxx-xy/stat/POSITION => 0-100

- {myhome}/{minido}/{home}/EXOxx-xy/cmnd/POSITION <= 0-100

- {myhome}/{minido}/{home}/EXOxx-x/stat/BRIGHTNESS => 0-100 (% 0 is smallest and increase by 2 up to 100)

- {myhome}/{minido}/{home}/EXOxx-x/cmnd/BRIGHTNESS <= 0-100 (% 0 is smallest and increase by 2 up to 100), > 100 is considered 100, bellow 0 is cosidered 0


## Configuration

Configuration enables adding  metadate for MINIDO items, which enables its better representation in the Home Assistant. Configuration is a JSON map object. 

The following types of configurations are most importent:
- **type** - This is the most importent part of the configuration, it defines how Home Assistent will see the MINIDO items. It supports the followin values: temperature, dimmer, switch, binary_sensor, motion_sensor, light_sensor, button_short, button_long, light, cover. By default all minido items are configured as **switch**.  
- label = auto()
- location = auto()

Additional types of configurations are as followes:
- typediscovery = auto()
- brightness = auto()
- discovery = auto()
- discoverymode = auto()
- devicediscoverymode = auto()
- cover = auto()
- covertime = auto()

**Please Note:** _Configuration inhearits within the trea of MINIDO items. E.g. any configuration for EXI01, would be applicable also for EXI01-1, EXI01-2, etc. Any configuration for EXO would be applicable for EXO01, EXO02, etc, so effectively for EXO01-1, EXO01-2, ..., EXO02-1, EXO02-2, etc._
