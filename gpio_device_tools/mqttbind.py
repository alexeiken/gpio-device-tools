#!/usr/bin/env python
import atexit
import logging
import os
import sys
from optparse import OptionParser

import paho.mqtt.client as mqtt
import time

import config
from write import gpio_write

MQTT_GPIO_BINDING_CFG = 'MQTT_GPIO_BINDING_CFG'

USAGE = '\n' \
        '  mqttgpiobind --topic <topic name> [--invert] --pin <ID> --mqtt-config <MQTT config file>\n' \
        '  mqttgpiobind --config <binding and MQTT config file>\n' \
        '  mqttgpiobind -h | --help'


def main(argv):
    if len(argv) > 1:
        options = parse_options(argv)
    elif MQTT_GPIO_BINDING_CFG in os.environ:
        options = config.ConfigItem()
        options.mqtt_topic = None
        options.mqtt_cfg_file = None
        options.cfg_file = os.environ[MQTT_GPIO_BINDING_CFG]
        options.log_file = None
        options.verbose = True

        init_logging(options)
    else:
        sys.stdout.write("Usage:{}".format(USAGE))
        sys.exit()

    logging.info('Starting MqttGpioBindingService with PID \'%s\'', os.getpid())

    option_binding = None
    if options.mqtt_topic is not None:
        option_binding = config.create_binding_cfg(
            options.mqtt_topic,
            options.gpio_pin,
            options.invert)

    mqtt_bind = MqttGpioBindingService(
        option_binding=option_binding,
        cfg_file=options.cfg_file,
        mqtt_cfg_file=options.mqtt_cfg_file)

    atexit.register(cleanup, mqtt_bind)
    mqtt_bind.run()


def cleanup(mqtt_daemon):
    logging.debug('Starting cleanup...')
    mqtt_daemon.disconnect()
    logging.info('Cleanup finished')


def parse_options(argv):
    parser = OptionParser(usage=USAGE)
    parser.set_defaults(mqtt_topic=None)
    parser.set_defaults(mqtt_cfg_file=None)
    parser.set_defaults(cfg_file=None)
    parser.set_defaults(log_file=None)
    parser.add_option('-p', '--pin',
                      dest='gpio_pin', metavar='<ID>',
                      help='ID of the GPIO pin to bind the MQTT topic to')
    parser.add_option('-i', '--invert',
                      action='store_const', dest='invert', const=True,
                      help='inverts the value received from the MQTT topic before it is written to the GPIO pin')
    parser.add_option('-t', '--topic',
                      dest='mqtt_topic', metavar='<MQTT topic>',
                      help='the MQTT topic to bind to the GPIO pin')
    parser.add_option('-m', '--mqtt-config',
                      dest='mqtt_cfg_file', metavar='<MQTT config file>',
                      help='the MQTT server configuration in file')
    parser.add_option('-g', '--config',
                      dest='cfg_file', metavar='<config file>',
                      help='the binding and MQTT server configuration in file')
    parser.add_option('-l', '--log-file',
                      dest='log_file', metavar='<logfile>',
                      help='logs to the given file')
    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose', default=False,
                      help='enables detailed logging')
    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.error('Unsupported arguments: ' + ', '.join(args))

    if options.mqtt_topic is None and options.cfg_file is None:
        parser.error('The option --topic is not defined')
    if options.gpio_pin is None and options.cfg_file is None:
        parser.error('The option --pin is not defined')
    if options.mqtt_cfg_file is None and options.cfg_file is None:
        parser.error('The MQTT server configuration file is missing')
    if options.mqtt_topic is not None and options.cfg_file is not None:
        parser.error('The binding may either be defined by command line arguments or in a config file')

    init_logging(options)

    logging.debug('Command line options: %s', options)

    return options


def init_logging(options):
    if options.log_file is not None:
        logging.getLogger().addHandler(logging.FileHandler(options.log_file))
        logging.getLogger().setLevel(logging.INFO)
    if options.verbose:
        logging.getLogger().addHandler(logging.StreamHandler())
        logging.getLogger().setLevel(logging.DEBUG)


class MqttGpioBindingService():

    def __init__(self, option_binding=None, mqtt_cfg_file=None, cfg_file=None):
        self.__cfg_file = cfg_file
        self.__cfg_file_time = None

        self.__bindings = []
        if option_binding is not None:
            self.__bindings.append(option_binding)

        if mqtt_cfg_file is not None:
            self.__mqtt_cfg = config.MqttServerConfigReader(cfg_file=mqtt_cfg_file)
        else:
            self.__cfg = config.MqttBindingConfigReader(cfg_file=cfg_file)
            self.__mqtt_cfg = config.MqttServerConfigReader(cfg_file=cfg_file)

        self.__client = None
        self.__connected = False

        self.reload_bindings()

    def reload_bindings(self):
        if self.__cfg_file is None:
            self.log_bindings()
            return

        cfg = config.MqttBindingConfigReader(self.__cfg_file)
        self.__cfg_file_time = time.ctime(
            os.path.getmtime(self.__cfg_file))

        self.__bindings = []
        self.__bindings.extend(cfg.bindings)

        self.log_bindings()

    def log_bindings(self):
        logging.info('Initialize Bindings:')

        for binding in self.__bindings:
            if binding.invert:
                logging.info('Topic \'%s\' -> invert value -> GPIO Pin \'%s\'',
                             binding.topic, binding.pin)
            else:
                logging.info('Topic \'%s\' -> GPIO Pin \'%s\'',
                             binding.topic, binding.pin)

    def get_actions(self, topic):
        for binding in self.__bindings:
            if topic == binding.topic:
                return binding.pin, binding.invert

        return None, None

    def on_connect(self, client, userdata, flags, rc):
        self.__connected = True
        logging.info('Connected with result code: %d', rc)

        for binding in self.__bindings:
            self.__client.subscribe(binding.topic)
            logging.info('Subscribed to topic: %s',
                         binding.topic)

    def on_disconnect(self, mqttc, userdata, rc):
        self.__connected = False
        logging.info('Disconnected from MQTT server')

    def on_message(self, client, userdata, msg):
        if msg.topic is None or msg.payload is None:
            return

        pin, invert = self.get_actions(msg.topic)
        if pin is None:
            return

        message = msg.payload.strip()

        logging.debug('Value received from topic \'%s\': \'%s\'',
                      msg.topic, message)

        if config.is_boolean_value(message):
            value = self.str_2_one_zero(message, invert)

            logging.info('Writing value %s to pin \'%s\'',
                         value, pin)

            gpio_write(pin, value)

    def run(self):
        self.__client = mqtt.Client()

        logging.info('Connecting to MQTT server %s',
                     self.__mqtt_cfg.mqtt_host)
        self.__client.connect(
            self.__mqtt_cfg.mqtt_host,
            self.__mqtt_cfg.port,
            self.__mqtt_cfg.keepalive)

        self.__client.on_connect = self.on_connect
        self.__client.on_disconnect = self.on_disconnect
        self.__client.on_message = self.on_message

        self.__client.loop_forever()

    def disconnect(self):
        if self.__client is not None and self.__connected:
            logging.info('Disconnecting from MQTT server...')
            self.__client.disconnect()

    @staticmethod
    def str_2_one_zero(value, invert=False):
        result = config.get_boolean_value(value)
        if invert:
            result = not result

        if result:
            return '1'
        else:
            return '0'


if __name__ == '__main__':
    main(sys.argv[1:])