# minido2mqtt


![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

## About

Minido and D2000 by AnD bridge to MQTT with HomeAssistant naming convencion. It contains 2 microservices:

minido_link is TCPCLient/Serial to MQTT Low handler

minido_home is low level to home level bridge



### LOW protocol interface is defined

{myhome}/{minido}/{low}/{read} => Minido package in binary format

{myhome}/{minido}/{low}/{write} <= Minido package in binary format


### HOME protocol interface is defined as follows:

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

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
