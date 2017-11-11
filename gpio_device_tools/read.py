#!/usr/bin/python
import os
import sys
from optparse import OptionParser

import outchannel
from gpio_device_tools import config


def main(argv):
    sensor_cfgs = parse_options(argv)
    for sensor_cfg in sensor_cfgs:
        read_and_output_sensor_data(sensor_cfg)


def parse_options(argv):
    usage = '\n' \
            '  gpioread --sensor <sensor> [--id <ID>] [--label <label>] ' \
            '[(--text | --csv <CSV file> | --xml | --json | --mqtt <MQTT config file>  [--hostname <hostname>])] ' \
            '[--outfile <output file>]\n' \
            '  gpioread --config <sensor and MQTT config file>\n' \
            '  gpioread -h | --help'

    parser = OptionParser(usage=usage)
    parser.set_defaults(hostname='hostname')
    parser.set_defaults(out_format=config.TEXT_FORMAT)
    parser.set_defaults(out_channel=config.CONSOLE_CHANNEL)
    parser.set_defaults(id=None)
    parser.set_defaults(label='Label')
    parser.set_defaults(mqtt_cfg_file=None)
    parser.set_defaults(cfg_file=None)
    parser.add_option('-s', '--sensor',
                      dest='sensor', metavar='<sensor>',
                      help='sensor type, optionally with address')
    parser.add_option('-l', '--label',
                      dest='label', metavar='<label>',
                      help='outputs sensor data with the given label')
    parser.add_option('-i', '--id',
                      dest='id', metavar='<ID>',
                      help='outputs sensor data with the given id')
    parser.add_option('-t', '--text',
                      action='store_const', dest='out_format', const=config.TEXT_FORMAT,
                      help='outputs sensor data in a text format')
    parser.add_option('-c', '--csv',
                      dest='csv_file', metavar='<CSV file>',
                      help='outputs sensor data as a single line in a CSV format and appends it to CSV_FILE')
    parser.add_option('-x', '--xml',
                      action='store_const', dest='out_format', const=config.XML_FORMAT,
                      help='outputs sensor data in a XML format')
    parser.add_option('-j', '--json',
                      action='store_const', dest='out_format', const=config.JSON_FORMAT,
                      help='outputs sensor data in a JSON format')
    parser.add_option('-o', '--outfile',
                      dest='out_file', metavar='<output file>',
                      help='writes the sensor data to given file')
    parser.add_option('-m', '--mqtt',
                      dest='mqtt_cfg_file', metavar='<MQTT config file>',
                      help='writes the sensor data to the MQTT server defined in the config file')
    parser.add_option('-n', '--hostname',
                      dest='hostname', metavar='HOSTNAME',
                      help='defines the hostname of this computer')
    parser.add_option('-g', '--config',
                      dest='cfg_file', metavar='<config file>',
                      help='the sensor and MQTT server configuration in config file')
    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose', default=False,
                      help='enables verbose mode')
    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.error('Unsupported arguments: ' + ', '.join(args))

    if options.sensor is None and options.cfg_file is None:
        parser.error('Either options --sensor or --config have to be defined')

    if options.sensor is not None:
        splitted = options.sensor.split(':', 2)
        options.sensor_type = splitted[0]
        if len(splitted) > 1:
            options.sensor_param = splitted[1]
        else:
            options.sensor_param = ''

    if options.csv_file is not None:
        options.out_format = config.CSV_FORMAT
        options.out_file = options.csv_file
        options.out_channel = config.CSV_FILE_CHANNEL
    elif options.out_file is not None:
        options.out_channel = config.FILE_CHANNEL
    if options.mqtt_cfg_file is not None:
        options.out_channel = config.MQTT_CHANNEL

    if options.verbose:
        print 'Options: ', options

    if options.cfg_file is not None:
        # sensor config parsed from file
        cfg = config.SensorConfigReader(
            options.cfg_file,
            options.mqtt_cfg_file,
            options.verbose)
        return cfg.sensors
    else:
        # sensor config given by command line options
        return [options]


def read_and_output_sensor_data(sensor_cfg):
    if sensor_cfg.verbose:
        print 'Sensor: ' , sensor_cfg.sensor_type
        if not sensor_cfg.sensor_param == '':
            print 'Parameter: ' + sensor_cfg.sensor_param
        if sensor_cfg.out_channel == config.CSV_FILE_CHANNEL:
            print 'CSV file channel'
            print 'CSV file: ', sensor_cfg.out_file
        if sensor_cfg.out_channel == config.MQTT_CHANNEL:
            print 'MQTT channel'
            print 'Config file: ', sensor_cfg.mqtt_cfg_file
        if sensor_cfg.out_file is not None:
            print 'Output file  : ', sensor_cfg.out_file
            print 'Output format: ', sensor_cfg.out_format

    sens = None

    if sensor_cfg.sensor_type.lower() == 'dummy':
        import sensor
        sens = sensor.DummySensor(
            id=sensor_cfg.id,
            label=sensor_cfg.label)
    elif sensor_cfg.sensor_type.lower() == 'bmp085':
        import bmp085
        sens = bmp085.BMP085Sensor(
            param=sensor_cfg.sensor_param,
            id=sensor_cfg.id,
            label=sensor_cfg.label,
            verbose=sensor_cfg.verbose)
    elif sensor_cfg.sensor_type.lower() == 'dht11':
        import dht
        sens = dht.DHT(
            sensor_type='11',
            pin=sensor_cfg.sensor_param,
            id=sensor_cfg.id,
            label=sensor_cfg.label,
            verbose=sensor_cfg.verbose)
    elif sensor_cfg.sensor_type.lower() == 'dht22':
        import dht
        sens = dht.DHT(
            sensor_type='22',
            pin=sensor_cfg.sensor_param,
            id=sensor_cfg.id,
            label=sensor_cfg.label,
            verbose=sensor_cfg.verbose)
    elif sensor_cfg.sensor_type.lower() == 'dht2302':
        import dht
        sens = dht.DHT(
            sensor_type='2302',
            pin=sensor_cfg.sensor_param,
            id=sensor_cfg.id,
            label=sensor_cfg.label,
            verbose=sensor_cfg.verbose)
    elif sensor_cfg.sensor_type.lower() == 'htu21':
        import htu21d
        sens = htu21d.HTU21Sensor(
            param=sensor_cfg.sensor_param,
            id=sensor_cfg.id,
            label=sensor_cfg.label,
            verbose=sensor_cfg.verbose)
    elif sensor_cfg.sensor_type.lower() == 'ds1820':
        import ds1820
        sens = ds1820.DS1820Sensor(
            sens_id=sensor_cfg.sensor_param,
            id=sensor_cfg.id,
            label=sensor_cfg.label,
            verbose=sensor_cfg.verbose)

    if sens is not None:
        if sensor_cfg.out_channel == config.MQTT_CHANNEL:
            channel = outchannel.MqttChannel(
                mqtt_cfg_file=sensor_cfg.mqtt_cfg_file,
                hostname=sensor_cfg.hostname,
                verbose=sensor_cfg.verbose)
        elif (sensor_cfg.out_channel == config.FILE_CHANNEL) \
                and (sensor_cfg.out_file is not None):
            channel = outchannel.FileChannel(
                out_format=sensor_cfg.out_format,
                fn=sensor_cfg.out_file,
                verbose=sensor_cfg.verbose)
        elif sensor_cfg.out_channel == config.CSV_FILE_CHANNEL:
            channel = outchannel.CSVFileChannel(
                fn=sensor_cfg.out_file,
                verbose=sensor_cfg.verbose)
        else:
            channel = outchannel.ConsoleChannel(
                out_format=sensor_cfg.out_format)

        channel.output(sens)
    else:
        print 'Unsupported sens ', sensor_cfg.sensor_type


if __name__ == '__main__':
    main(sys.argv[1:])
