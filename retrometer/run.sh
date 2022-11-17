#!/usr/bin/with-contenv bashio

echo "Starting retrometer add on..."

# Declare variables
declare mqttuser
declare mqttpasswd
declare mqtttopic
declare m3pertick


## Get the 'mqttuser' key from the user config options.
mqttuser=$(bashio::config 'mqttuser')
mqttpasswd=$(bashio::config 'mqttpasswd')
mqtttopic=$(bashio::config 'mqtttopic')
m3pertick=$(bashio::config 'm3pertick')

python3 /retrometer/measure_gas.py --mqttuser ${mqttuser} --mqttpasswd ${mqttpasswd} --mqtttopic ${mqtttopic} --m3pertick ${m3pertick} -v
