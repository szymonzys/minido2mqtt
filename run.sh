#!/usr/bin/with-contenv bashio
set -e

LINKMODE=$(bashio::config 'minidoLinkType')
TTY=$(bashio::config 'minidoSerial')
SERVER=$(bashio::config 'minidoTCPAddress')
PORT=$(bashio::config 'minidoTCPPort')
HOMETOPIC=$(bashio::config 'homeProtocolTopic')
DISCOVERYTOPIC=$(bashio::config 'discoveryTopic')
MQTTBROKER=$(bashio::config 'mqttBrokerAddress')
MQTTPORT=$(bashio::config 'mqttPort')
MQTTUSER=$(bashio::config 'mqttUser')
MQTTPASSWORD=$(bashio::config 'mqttPassword')
MQTTHOMEID=$(bashio::config 'homeid')
MQTTTOPIC="minido"
BRIDGETOPIC=$(bashio::config 'lowProtocolTopic') 
READTOPIC=$(bashio::config 'readTopic') 
WRITETOPIC=$(bashio::config 'writeTopic')

LINKPARAMETERS=""
if [ $LINKMODE = "serial" ]; then
  if [ $TTY != "" ]; then  
    LINKPARAMETERS="--tty=$TTY"
  fi
fi

if [ $LINKMODE = "tcpclient" ]; then
  if [ $SERVER != "null" ]; then  
    LINKPARAMETERS="$LINKPARAMETERS --server=$SERVER"
  fi
  if [ $PORT != "null" ]; then  
    LINKPARAMETERS="$LINKPARAMETERS --port=$PORT"
  fi
fi

MQTTUSERPARAMETERS=""
if [ $MQTTUSER != "null" ]; then  
  MQTTUSERPARAMETERS="$MQTTUSERPARAMETERS --mqttUser=$MQTTUSER"
fi
if [ $MQTTPASSWORD != "null" ]; then  
  MQTTUSERPARAMETERS="$MQTTUSERPARAMETERS --mqttPassword=$MQTTPASSWORD"
fi

MQTTPARAMETERS="--mqttHomeId=$MQTTHOMEID --mqttTopic=$MQTTTOPIC --bridgeTopic=$BRIDGETOPIC --readTopic=$READTOPIC --writeTopic=$WRITETOPIC"
if [ $MQTTBROKER != "null" ]; then  
  MQTTUSERPARAMETERS="$MQTTUSERPARAMETERS --mqttBroker=$MQTTBROKER"
fi
if [ $MQTTPORT != "null" ]; then  
  MQTTUSERPARAMETERS="$MQTTUSERPARAMETERS --mqttPort=$MQTTPORT"
fi
HOMEPARAMETERS="--homeTopic=$HOMETOPIC --discoveryTopic=$DISCOVERYTOPIC"



echo "Minido 2 MQTT Bridge!"
echo "Connection mode: ${LINKMODE}"
echo "LINK Params: ${LINKPARAMETERS}"
echo "MQTT Params: ${MQTTPARAMETERS}"
echo "HOME Params: ${HOMEPARAMETERS}"

echo "Starting LINK ..."
python3 /minido_link.py ${MQTTUSERPARAMETERS} ${MQTTPARAMETERS} ${LINKMODE} ${LINKPARAMETERS} &
echo "Starting BRIDGE ..."
python3 /mqtt_home.py ${MQTTUSERPARAMETERS} ${MQTTPARAMETERS} ${HOMEPARAMETERS} &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?