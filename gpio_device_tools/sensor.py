# -*- coding: utf-8 -*-
import os
from abc import ABCMeta, abstractmethod
from string import Template
from datetime import datetime
import config

DUMMY_STR = 'dummy'

TPL_TEMP = 'temp'
TPL_TEMP_HUM = 'temp_hum'
TPL_TEMP_PRES_ALT = 'temp_pres_alt'

def parse_number(param, default=0):
    try:
        if param is not None:
            return int(param)
        else:
            return default
    except ValueError:
        return default


class Sensor:
    __metaclass__ = ABCMeta

    def __init__(self, param, id, label='Label', verbose=False):
        self.base_dir = os.path.dirname(__file__)
        if id is None or id == '':
            self.id = self.generate_id(param)
        else:
            self.id = id
        self.label = label
        self.verbose = verbose

    @abstractmethod
    def generate_id(self, param):
        pass

    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def template_type(self):
        pass

    @abstractmethod
    def sensor_data_types(self):
        pass

    @abstractmethod
    def dictionary(self):
        pass

    @abstractmethod
    def csv_header(self):
        pass

    @abstractmethod
    def csv_line(self):
        pass

    def text_format(self):
        return self.fill_template('txt')

    def xml_format(self):
        return self.fill_template('xml')

    def json_format(self):
        return self.fill_template('json')

    def fill_template(self, tpl_file_suffix):
        file = open(os.path.join(
            self.base_dir,
            config.tpl_file_path_name.format(
                self.template_type(),
                tpl_file_suffix)))

        src = Template(file.read())
        return src.safe_substitute(self.dictionary())


class DummySensor(Sensor):

    def __init__(self, id=None, label=DUMMY_STR):
        Sensor.__init__(self, None, id, label, False)
        self.time = '2016-08-02T22:27:49'
        self.temperature = 20.12345

    def generate_id(self, param):
        return DUMMY_STR

    def type(self):
        return DUMMY_STR

    def template_type(self):
         return TPL_TEMP

    def sensor_data_types(self):
        return ['temperature']

    def dictionary(self):
        return dict(
            type=self.type(),
            id=self.id,
            label=self.label,
            time=self.time,
            temperature='{:.2f}'.format(self.temperature),
            temperatureUnit='C')

    def csv_header(self):
        return "Time;Temperature °C\n"

    def csv_line(self):
        return "{};{:.2f}\n".format(
            self.time,
            self.temperature)
