# Home Assistant Add-on: MINIDO2MQTT

This is Home Assistent addon for using AnB (Belgium) Minido or D2000 system within Home Assistent as MQTT devices. 

## MINIDO/D2000



## Services

It contains 2 microservices:

- **minido_link** is link service between TCPCLient/Serial conectivity to MINIDO and MQTT. It directly transmits minido packages in its raw/binary format and place it into the MQTT topic. It constitutes **LOW protocol**.

- **minido_home** is bridge service between LOW protocl and [Home Assistant MQTT](https://www.home-assistant.io/integrations/mqtt/) item. It allowes for storing configurations for each MINIDO item. It supports [Home Assistant discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery) messages for configured items. It constitutes **HOME protocol**.



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

Configuration enables adding metadata for MINIDO items, which enables its better representation in the Home Assistant. Configuration is a JSON map object. 

The following types of configurations are most importent:
- **type** - This is the most importent part of the configuration, it defines how Home Assistent will discover each MINIDO item. It supports the followin values: **temperature, dimmer, switch, binary_sensor, motion_sensor, light_sensor, button_short, button_long, light, cover**. Type will define also what By default all minido items are configured as **switch**.  
- **label** - This is human friendly description of the item eg. _"Main Light"_
- **location** - This is human friendly description of the item location eg. _"Kitchen"_

**Please Note:** _Bridge service can automaticly recognize values and automaticli assign the type configuration such as: dimer or temperature based on the analyses of the values recieved over the bus._

Additional types of configurations are as followes:
- **discoverymode** - configures which items are being visible in Home Assistant discovery
    - all - all items
    - label - items with label only
    - none - non of the items.
- **devicediscoverymode** - configures how items are being agregated into devices during Home Assistant discovery process
    - minido - items are agregated as phisicly exists into minido unites 
    - virtual - items are agregated into virtual devices representig location
    - none - no agregation into devices
- **cover** - allowes to agregate two MINIDO items into Home Assistant cover. Configuration is set as virtual item e.g. EXO09-12 - agregates item EXO09-1 and EXO09-2 into virtual cover. The first item represents movement up, second down.
- **covertime** - defines time in seconds required for the item to perform the full movement (full clouser or full open), in some cases, the movement down is faster then movement up so it has to be defined for each MINIDO item agregated within the cover virtual item.

Advanced configurations which are unliekly to be set by the users:
- brightness - store value of the brighness, for dimmer lights. Set automaticly by service, there is no need to set it manually.
- discovery - defines the setings for Home Assistent discovery. Discovery info are merged with type specific dyscovery.
- typediscovery - defines the type of the object used in the Home Automation discovery. Map containing type specific discovery information. Data are merged with discovery setting.

**Please Note:** _Configuration inhearits within the tree of MINIDO items. E.g. any configuration for EXI01, would be applicable also for EXI01-1, EXI01-2, etc. Any configuration for EXO would be applicable for EXO01, EXO02, etc, so effectively for EXO01-1, EXO01-2, ..., EXO02-1, EXO02-2, etc. Configuration inheritance does not work for agregate virtual cover items, configuration for EXO09-12 is not inhearited by EXO09-1 nor EXO09-2._ 
