import ConfigParser
import os

import config
from abc import ABCMeta, abstractmethod


class OutputChannel:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)

    @abstractmethod
    def output(self, sensor):
        pass

    def data(self, sensor, format):
        if format == config.XML_FORMAT:
            return sensor.xml_format()
        elif format == config.JSON_FORMAT:
            return sensor.json_format()
        else:
            return sensor.text_format()

    @staticmethod
    def make_dir(fn):
        if not os.path.dirname(fn):
            return
        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))


class ConsoleChannel(OutputChannel):

    def __init__(self, out_format=config.TEXT_FORMAT, verbose=False):
        super(ConsoleChannel, self).__init__()
        self.__out_format = out_format

    def output(self, sensor):
        print self.data(sensor, self.__out_format)


class FileChannel(OutputChannel):

    def __init__(self, out_format=config.JSON_FORMAT, fn=None, verbose=False):
        super(FileChannel, self).__init__()
        self.__out_format = out_format
        self.__fn = fn
        self.__verbose = verbose

    def output(self, sensor):
        if self.__fn is None:
            self.__fn = sensor.id()

        if self.__verbose:
            print "DBG: Output to file: {}".format(
                    self.__fn)

        self.make_dir(self.__fn)

        fd = open(self.__fn, 'w')
        fd.write(self.data(sensor, self.__out_format))
        fd.close()


class CSVFileChannel(OutputChannel):

    def __init__(self, fn=None, verbose=False):
        super(CSVFileChannel, self).__init__()
        self.__fn = fn
        self.__verbose = verbose

    def output(self, sensor):
        if os.path.isfile(self.__fn):
            if self.__verbose:
                print "DBG: Append to existing CSV file: {}".format(
                    self.__fn)

            fd = open(self.__fn, 'a')
            fd.write(sensor.csv_line())
            fd.close()
        else:
            if self.__verbose:
                print "DBG: Creating new CSV file: {}".format(
                    self.__fn)

            self.make_dir(self.__fn)

            fd = open(self.__fn, 'w')
            fd.write(sensor.csv_header())
            fd.write(sensor.csv_line())
            fd.close()


class MqttChannel(OutputChannel):

    def __init__(self, mqtt_cfg_file=None, hostname='hostname', verbose=False):
        super(MqttChannel, self).__init__()
        self.__hostname = hostname
        self.__verbose = verbose
        self.__mqtt_cfg = config.MqttServerConfigReader(cfg_file=mqtt_cfg_file)

    def output(self, sensor):
        dictionary = sensor.dictionary()

        msgs = []

        for type in sensor.sensor_data_types():
            topic = config.mqtt_sensor_topic_format.format(
                self.__hostname, type, sensor.id)

            msg = {'topic':topic,
                   'payload':dictionary[type],
                   'qos':self.__mqtt_cfg.qos,
                   'retain':self.__mqtt_cfg.retain}
            msgs.append(msg)

            if self.__verbose:
                print "DBG: Publishing value '{}' to topic '{}'".format(
                    dictionary[type], topic)

        import paho.mqtt.publish as publish
        publish.multiple(msgs,
                         hostname=self.__mqtt_cfg.mqtt_host,
                         port=self.__mqtt_cfg.port,
                         client_id=self.__mqtt_cfg.client_id,
                         keepalive=self.__mqtt_cfg.keepalive)

        if self.__verbose:
            print "DBG: Messages published"