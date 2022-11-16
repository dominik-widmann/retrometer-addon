#!/usr/bin/with-contenv bashio

echo "Starting retrometer add on..."

# Declare variables
declare mqttuser
declare mqttpasswd

## Get the 'mqttuser' key from the user config options.
mqttuser=$(bashio::config 'mqttuser')
mqttpasswd=$(bashio::config 'mqttpasswd')

## Print the config the user supplied"
bashio::log.info "Mqtt user: ${mqttuser}, passwd: ${mqttpasswd}"

python3 /retrometer/measure_gas.py --mqttuser ${mqttuser} --mqttpasswd ${mqttpasswd} -v
