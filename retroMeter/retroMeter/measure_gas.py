#!/usr/bin/env python
from smbus import SMBus
import time
from src.magnetometer import MMC5983MA
from src.retro_meter import RetroMeter
import paho.mqtt.client as mqtt
import json


m3perTick = 0.01

MQTT_OUTPUT_TOPIC = "meter/gas_volume"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to mqtt broker")
    else:
        print("Connection to mqtt broker failed with result code "+str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


if __name__ == "__main__":
    import argparse
    # Get the input args
    parser = argparse.ArgumentParser(
        description='Gas meter application that publishes gas meter readings to mqtt homeassistant.')
    parser.add_argument('--mqttuser', help='mqtt user')
    parser.add_argument('--mqttpasswd', help='mqtt user password')
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    # Setup mqtt connection
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(args.mqttuser, args.mqttpasswd)
    client.connect("homeassistant", 1883, 60)
    client.loop_start()

    # Setup meter
    i2cbus = SMBus(1)
    magnetometer = MMC5983MA(i2cbus)
    sample_time = 0.05
    max_period_time = 1.0  # seconds
    max_period_length = int(max_period_time/sample_time)
    min_amplitude = 20
    max_amplitude = 8000
    min_std = 50
    meter = RetroMeter(magnetometer, "x", max_period_length,
                       min_amplitude, max_amplitude, min_std, is_verbose=args.v)

    last_count = -1
    while(True):
        # Read measurements
        if meter.is_count_updated():
            count = meter.update_and_get_meter_ticks()

            # if count changed, publish an mqtt message
            if last_count != count:
                last_count = count  # store new value
                volume = count * m3perTick

                # publish value over mqtt
                client.publish(MQTT_OUTPUT_TOPIC, json.dumps(
                    {"volume": volume, "count": count}))

            time.sleep(sample_time)
