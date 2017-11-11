# -*- coding: utf-8 -*-
from datetime import datetime

from lib.Adafruit_BMP085 import BMP085

import config
from sensor import Sensor, parse_number, TPL_TEMP_PRES_ALT

BMP085_STR = 'bmp085'


class BMP085Sensor(Sensor):
    def __init__(self, param='0', id=None, label=BMP085_STR, verbose=False):
        Sensor.__init__(self, param, id, label, verbose)

        bus_nb = parse_number(param, 0)

        if self.verbose:
            print 'DBG: BMP085 sensor \'{}\' bus number {:d}'.format(
                label, bus_nb)

        bmp = BMP085(busnum=bus_nb)

        self.temperature = bmp.read_temperature()
        self.pressure = bmp.read_pressure()
        self.altitude = bmp.read_altitude()

    def generate_id(self, param):
        return '{}_{}'.format(parse_number(param, default=0), BMP085_STR)

    def type(self):
        return BMP085_STR

    def template_type(self):
        return TPL_TEMP_PRES_ALT

    def sensor_data_types(self):
        return ['temperature', 'pressure', 'altitude']

    def dictionary(self):
        return dict(
            type=self.type(),
            id=self.id,
            label=self.label,
            time=datetime.now().strftime(config.dt_format),
            temperature='{:.2f}'.format(self.temperature),
            temperatureUnit='C',
            pressure='{:.2f}'.format(self.pressure),
            pressureUnit='hPa',
            altitude='{:.2f}'.format(self.altitude),
            altitudeUnit='m')

    def csv_header(self):
        return 'Time;Temperature °C;Pressure hPa;Altitude m\n'

    def csv_line(self):
        return '{};{:.2f};{:.2f};{:.2f}\n'.format(
            datetime.now().strftime(config.dt_format),
            self.temperature,
            self.pressure,
            self.altitude)
