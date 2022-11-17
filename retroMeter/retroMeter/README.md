# retroMeter

## Setup
- enabled mosquitto mqtt broker on home assistant
- mqtt client connects to that
- added mqtt sensor for volume and template sensor for kWh in home assistant energy configuration
- enabled i2c via the haas i2c configurator add-on (protection disabled)
- configure mqtt credentials
- enable mqtt integration with mosquito
- setup dashboard:

### Configure mqtt sensor
```yaml 
# Gas volume
mqtt:
  sensor:
    - name: "gas_volume"
      state_topic: "meter/gas_volume"
      value_template: "{{ value_json.volume }}"
      unit_of_measurement: "m³"
      unique_id: "gas_volume0"
```