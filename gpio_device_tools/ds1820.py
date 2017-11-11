# -*- coding: utf-8 -*-
import io
import re
from datetime import datetime

from Adafruit_GPIO import Platform

import config
from sensor import Sensor, parse_number, TPL_TEMP

DS1820_STR = 'ds1820'


class DS1820Sensor(Sensor):

    def __init__(self, sens_dir=None, sens_id=None, sens_file=None, id=None,
                 label=DS1820_STR, verbose=False):
        Sensor.__init__(self, sens_id, id, label, verbose)

        if sens_dir is None or sens_file is None:

            if self.verbose:
                print 'DBG: CHIP platform detected: {}'.format(config.chip_platform)

            if sens_dir is None:
                if config.chip_platform:
                    sens_dir = config.chip_w1_dir
                else:
                    sens_dir = config.default_w1_dir
            if sens_file is None:
                if config.chip_platform:
                    sens_file = config.chip_w1_file
                else:
                    sens_file = config.default_w1_file

        if not sens_dir.endswith('/'):
            sens_dir += '/'

        if self.verbose:
            print 'DBG: DS1820 sensor \'{}\': {}{}'.format(
                label, sens_dir, sens_id)

        self.temperature = self.read_temp(sens_dir, sens_id, sens_file)

    def read_temp(self, sens_dir, sens_id, sens_file):
        path = sens_dir + sens_id + '/' + sens_file

        if self.verbose:
            print 'DBG: Path = {}'.format(path)

        temp = ''
        try:
            with io.open(path, "r") as f:
                line = f.readline()
                if self.verbose:
                    print 'DBG: Line 1 = {}'.format(line)

                if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                    line = f.readline()
                    if self.verbose:
                        print 'DBG: Line 2 = {}'.format(line)

                    m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                    if m:
                        temp = float(m.group(2)) / 1000.0
                        if self.verbose:
                            print 'DBG: Temperature = {:.2f} °C'.format(temp)
        except IOError as e:
            if self.verbose:
                print 'DBG: I/O error({0}): {1}'.format(e.errno, e.strerror)

        return temp

    def generate_id(self, sensor_ID):
        return '{}'.format(sensor_ID)

    def type(self):
        return DS1820_STR

    def template_type(self):
         return TPL_TEMP

    def sensor_data_types(self):
        return ['temperature']

    def dictionary(self):
        return dict(
            type=self.type(),
            id=self.id,
            label=self.label,
            time=datetime.now().strftime(config.dt_format),
            temperature='{:.2f}'.format(self.temperature),
            temperatureUnit='C')

    def csv_header(self):
        return 'Time;Temperature °C\n'

    def csv_line(self):
        return '{};{:.2f}\n'.format(
            datetime.now().strftime(config.dt_format),
            self.temperature)