import ConfigParser
import os
import re

# date format
dt_format = "%Y-%m-%dT%H:%M:%S"

# boolean states
_boolean_states = {'1': True, 'yes': True, 'y': True, 'true': True, 't': True, 'on': True, 'high': True,
                   '0': False, 'no': False, 'n': False, 'false': False, 'f': False, 'off': False, 'low': False}


def is_boolean_value(v):
    return v.lower() in _boolean_states


def get_boolean_value(v):
    if is_boolean_value(v):
        return _boolean_states[v.lower()]
    else:
        raise ValueError, 'Not a boolean value: {}'.format(str)

# Output format constants
TEXT_FORMAT = 'txt'
CSV_FORMAT = 'csv'
XML_FORMAT = 'xml'
JSON_FORMAT = 'json'
MQTT_FORMAT = 'mqtt'

_output_formats = {TEXT_FORMAT, CSV_FORMAT, XML_FORMAT, JSON_FORMAT, MQTT_FORMAT}

# Channel constants
CONSOLE_CHANNEL = 1
FILE_CHANNEL = 2
CSV_FILE_CHANNEL = 3
MQTT_CHANNEL = 4

tpl_file_path_name = "templates/{0}/template.{1}"

# 1-wire DS1820 defaults
default_w1_dir = '/sys/bus/w1/devices/'
default_w1_file = 'w1_slave'
chip_w1_dir = '/sys/bus/w1/devices'
chip_w1_file = 'eeprom'


def detect_chip():
    """ Detect the CHIP computer from Next Thing Co, this could also be used to other
        Allwinner Based SBCs
    """
    # Open cpuinfo
    with open('/proc/cpuinfo','r') as infile:
        cpuinfo = infile.read()

    # Match a line like 'Hardware        : Allwinner sun4i/sun5i Families'
    match = re.search('^Hardware\s+:.*$', cpuinfo,
                      flags=re.MULTILINE | re.IGNORECASE)

    if not match:
        return False
    if "sun4i/sun5i" in match.group(0):
        return True
    else:
        return False

chip_platform = detect_chip()

sensor_defaults = {
    'label': 'Label',
    'id': 'ID'
}

# MqttChannel defaults
mqtt_defaults = {
    'host': 'localhost',
    'port': '1883',
    'client_id': 'gpio-device-tools',
    'qos': '0',
    'retain': 'True',
    'keepalive': '60'
}

mqtt_bindings_defaults = {
    'inverted': '0'
}

mqtt_sensor_topic_format = 'sensor/{}/{}/{}'
mqtt_actuator_topic_format = 'actuator/{}/{}/{}'

class ConfigurationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ConfigItem():
    pass


class SensorConfigReader():

    def __init__(self, cfg_file=None, mqtt_cfg_file=None, verbose=False):
        if cfg_file is None:
            raise ConfigurationError('Config file not defined')

        if os.path.isabs(cfg_file):
            abs_file= cfg_file
        else:
            abs_file = os.path.abspath(cfg_file)

        conf = ConfigParser.SafeConfigParser(
            defaults=sensor_defaults,
            allow_no_value=True)

        if abs_file is not None and os.path.isfile(abs_file):
            with open(abs_file) as f:
                conf.readfp(f)
        else:
            raise ConfigurationError('Config file not found: {} '.format(
                abs_file))

        self.sensors = []

        try:
            if conf.has_option('default', 'output'):
                output = conf.get('default', 'output')
            else:
                raise ConfigurationError('Value \'output\' not defined in section [default]')

            if output.lower() not in _output_formats:
                raise ConfigurationError('Unsupported value \'{}\' for option \'output\' in section [default]'
                                         .format(output))

            if conf.has_option('default', 'file'):
                out_file = conf.get('default', 'file')
            else:
                out_file = None

            if conf.has_option('default', 'hostname'):
                hostname = conf.get('default', 'hostname')
            else:
                hostname = None

            if conf.has_option('default', 'verbose'):
                verbose = conf.getboolean('default', 'verbose')

            if output == CSV_FORMAT and out_file is None:
                raise ConfigurationError('Value \'file\' needs to be defined for CSV output')
            elif output == MQTT_FORMAT and hostname is None:
                raise ConfigurationError('Value \'hostname\' needs to be defined for MQTT output')

            if output == CSV_FORMAT:
                out_channel = CSV_FILE_CHANNEL
            elif output == MQTT_FORMAT:
                out_channel = MQTT_CHANNEL
            elif out_file is not None:
                out_channel = FILE_CHANNEL
            else:
                out_channel = CONSOLE_CHANNEL

            if out_channel == MQTT_CHANNEL and mqtt_cfg_file is None:
                mqtt_cfg_file = cfg_file
            else:
                mqtt_cfg_file = None

            i = 1
            section_prefix = 'sensor'

            while conf.has_section(section_prefix + str(i)):
                section = section_prefix + str(i)

                if conf.has_option(section, 'type'):
                    type = conf.get(section, 'type')
                else:
                    raise ConfigurationError('Value \'type\' not defined in section [{}]'.format(
                        section))

                if conf.has_option(section, 'param'):
                    param = conf.get(section, 'param')
                else:
                    param = None

                if conf.has_option(section, 'id'):
                    id = conf.get(section, 'id')

                if conf.has_option(section, 'label'):
                    label = conf.get(section, 'label')

                if conf.has_option(section, 'topic'):
                    topic = conf.get(section, 'topic')
                else:
                    topic = None

                sensor = ConfigItem()
                sensor.out_channel = out_channel
                sensor.out_file = out_file
                sensor.mqtt_cfg_file = mqtt_cfg_file
                sensor.hostname = hostname
                sensor.sensor_type = type
                sensor.sensor_param = param
                sensor.id = id
                sensor.label = label
                sensor.topic = topic
                sensor.verbose = verbose

                self.sensors.append(sensor)

                i += 1
        except ConfigParser.NoOptionError:
            pass


class MqttServerConfigReader():

    def __init__(self, cfg_file=None):
        conf = ConfigParser.SafeConfigParser(
            defaults=mqtt_defaults,
            allow_no_value=True)

        abs_file = None
        if os.path.isabs(cfg_file):
            abs_file= cfg_file
        else:
            abs_file = os.path.abspath(cfg_file)

        if abs_file is not None and os.path.isfile(abs_file):
            with open(abs_file) as f:
                conf.readfp(f)

        section = 'mqtt'
        if not conf.has_section('mqtt'):
            section = 'DEFAULT'

        if conf.has_option(section, 'host'):
            self.mqtt_host = conf.get(section, 'host')
        else:
            raise ConfigurationError('Value \'host\' is not defined')

        if conf.has_option(section, 'port'):
            self.port = conf.get(section, 'port')
        else:
            raise ConfigurationError('Value \'port\' is not defined')

        if conf.has_option(section, 'client_id'):
            self.client_id = conf.get(section, 'client_id')
        else:
            raise ConfigurationError('Value \'client_id\' is not defined')

        self.qos = conf.getint(section, 'qos')
        self.retain = conf.getboolean(section, 'retain')
        self.keepalive = conf.getint(section, 'keepalive')


class MqttBindingConfigReader():

    def __init__(self, cfg_file=None):
        if cfg_file is None:
            raise ConfigurationError('Config file not defined')

        if os.path.isabs(cfg_file):
            abs_file= cfg_file
        else:
            abs_file = os.path.abspath(cfg_file)

        conf = ConfigParser.SafeConfigParser(
            defaults=mqtt_bindings_defaults,
            allow_no_value=True)

        if abs_file is not None and os.path.isfile(abs_file):
            with open(abs_file) as f:
                conf.readfp(f)
        else:
            raise ConfigurationError('Config file not found: {}'.format(
                abs_file))

        self.bindings = []

        try:
            i = 1
            section_prefix = 'binding'

            while conf.has_section(section_prefix + str(i)):
                section = section_prefix + str(i)

                if conf.has_option(section, 'topic'):
                    topic = conf.get(section, 'topic')
                else:
                    raise ConfigurationError('Value \'topic\' not defined in section [{}]'.format(
                        section))

                if conf.has_option(section, 'pin'):
                    pin = conf.get(section, 'pin')
                else:
                    raise ConfigurationError('Value \'pin\' not defined in section [{}]'.format(
                        section))

                if conf.has_option(section, 'invert'):
                    inverted = conf.getboolean(section, 'invert')
                else:
                    inverted = False

                self.bindings.append(
                    create_binding_cfg(topic, pin, inverted)
                )

                i += 1
        except ConfigParser.NoOptionError:
            pass


def create_binding_cfg(topic, pin, invert):
    binding = ConfigItem()
    binding.topic = topic
    binding.pin = pin
    binding.invert = invert

    return binding
