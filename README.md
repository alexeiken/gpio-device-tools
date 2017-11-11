gpio-device-tools
=================

This package provides a set of tools for accessing devices connected to the GPIO
pins of credit card–sized single-board computers like the Raspberry Pi or C.H.I.P..
The goal of this project is to provide hardware independent tools (as far as
possible) for reading sensor data or controlling devices connected to the
computers using different communication buses like 1-Wire or I2C. The tools require
python 2.7 which is in general available for most of the Linux operating systems
of such computers.

The Arduino platform is not supported.

# Installation

Install python and other required python libraries. On my Raspberry Pi 2 and C.H.I.P.
I had to execute the following commands.

````

sudo apt-get update
sudo apt-get install python python-setuptools python-pip python-dev python-smbus

````

Get the code.

````

git clone https://github.com/alexeiken/gpio-device-tools.git

````

Install the tools using setup.py.

````

sudo python setup.py install

````

# Tools

* __gpioread__:
Reads data from various sensors connected to the GPIO pins and outputs the data
in different data formats like JSON, XML or CSV. In addition to that the data
can also be published on a MQTT broker.

* __gpiowrite__:
Writes bit values to GPIO pins.

* __mqttgpiobind__:
Subscribes to topics on a MQTT server and writes received boolean values to GPIO
pins.


## gpioRead

### Usage

```
gpioread --sensor <sensor> [--id <ID>] [--label <label>] [(--text | --csv <CSV file> | --xml | --json | --mqtt <MQTT config file>  [--hostname <hostname>])] [--outfile <output file>]
gpioread --config <sensor and MQTT config file>
gpioread -h | --help

Options:
  -h, --help            show this help message and exit
  -s <sensor>, --sensor=<sensor>
                        sensor type, optionally with address
  -l <label>, --label=<label>
                        outputs sensor data with the given label
  -i <ID>, --id=<ID>    outputs sensor data with the given id
  -t, --text            outputs sensor data in a text format
  -c <CSV file>, --csv=<CSV file>
                        outputs sensor data as a single line in a CSV format
                        and appends it to CSV_FILE
  -x, --xml             outputs sensor data in a XML format
  -j, --json            outputs sensor data in a JSON format
  -o <output file>, --outfile=<output file>
                        writes the sensor data to given file
  -m <MQTT config file>, --mqtt=<MQTT config file>
                        writes the sensor data to the MQTT server defined in
                        the config file
  -n HOSTNAME, --hostname=HOSTNAME
                        defines the hostname of this computer
  -g <config file>, --config=<config file>
                        the sensor and MQTT server configuration in config
                        file
  -v, --verbose         enables verbose mode
```

### Supported sensors and hardware

Sensor | Bus | Data | Sensor ID | Tested on Hardware
--- | --- | --- | --- | ---
BMP085 | I2C | Temperature, Barometric Pressure, Altitude | bmp085 | C.H.I.P.
HTU21D(F) | I2C | Temperature, Humidity | htu21d | C.H.I.P.
DHT11 | I2C | Temperature, Humidity | dht11 | -
DHT22 | I2C | Temperature, Humidity | dht22 | Raspberry Pi 2
AM2302 | I2C | Temperature, Humidity | dht2302 | -
DS1820 | 1-Wire | Temperature | ds1820_fs | Raspberry Pi 2

### Examples

## gpioWrite

Writes bit values to GPIO pins.

### Usage

```
gpiowrite --pin <ID> <value> [--verbose]
gpiowrite -h | --help

Options:
  -h, --help            show this help message and exit
  -p <ID> <value>, --pin=<ID> <value>
                        ID of the GPIO pin and value to be written to the pin:
                        HIGH/LOW or true/false or 1/0
  -v, --verbose         enables verbose mode
```

## mqttgpiobind

Subscribes to topics on a MQTT server and writes received boolean values to GPIO pins.

A boolean value may be one of the following strings:

* '1' / '0'
* 'true' / 'false'
* 't' / 'f'
* 'yes' / 'no'
* 'y' / 'n'
* 'on' / 'off'

### Usage

```
mqttgpiobind --topic <topic name> [--invert] --pin <ID> --mqtt-config <MQTT config file>
mqttgpiobind --config <binding and MQTT config file>
mqttgpiobind -h | --help

Options:
  -h, --help            show this help message and exit
  -p <ID>, --pin=<ID>   ID of the GPIO pin to bind the MQTT topic to
  -i, --invert          inverts the value received from the MQTT topic before
                        it is written to the GPIO pin
  -t <MQTT topic>, --topic=<MQTT topic>
                        the MQTT topic to bind to the GPIO pin
  -m <MQTT config file>, --mqtt-config=<MQTT config file>
                        the MQTT server configuration in file
  -g <config file>, --config=<config file>
                        the binding and MQTT server configuration in file
  -l <logfile>, --log-file=<logfile>
                        logs to the given file
  -v, --verbose         enables detailed logging
```

### Examples

In the first example the MQTT topic `actuator/chip1/relay/1` is bound to GPIO
pin `XIO-P4`. The bit values received on the topic are inverted before the are
written to the GPIO pin (option `-i`). The MQTT server is defined in config file
`/home/chip/mqtt.cfg`.

```
mqttgpiobind -p XIO-P4 -i -t actuator/chip1/relay/1 -m /home/chip/mqtt.cfg
```

In case multiple bindings need to be defined the configuration has to be provided
in a binding config file together with the MQTT configuration.

```
mqttgpiobind -g /home/chip/binding.cfg -v
```

#### MQTT Configuration File Example

```
[mqtt]
# address of the broker to connect to. Defaults to localhost.
host = localhost
# port of the address broker to connect to. Defaults to 1883.
port = 1883

# MQTT client id
client_id = chip

# quality of service
# 0 – at most once
# 1 – at least once
# 2 – excatly once
qos = 2

# 'true' means that the broker will keep the message even after sending it
# to all current subscribers
retain = true

keepalive = 60
```

#### Binding Configuration File Example

```
[binding1]
topic = actuator/chip1/relay/1
pin = XIO-P4
invert = true

[binding2]
topic = actuator/chip1/relay/2
pin = XIO-P5
invert = true

[mqtt]
# address of the broker to connect to. Defaults to localhost.
host = localhost
# port of the address broker to connect to. Defaults to 1883.
port = 1883

# MQTT client id
client_id = chip

# quality of service
# 0 – at most once
# 1 – at least once
# 2 – excatly once
qos = 2

# 'true' means that the broker will keep the message even after sending it
# to all current subscribers
retain = true

keepalive = 60
```