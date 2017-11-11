# -*- coding: utf-8 -*-
from datetime import datetime

import config
from sensor import Sensor, parse_number, TPL_TEMP_HUM
import Adafruit_DHT

DHT_STR = 'dht'


class DHT(Sensor):

    def __init__(self, sensor_type='22', pin='4', id=None, label=DHT_STR, verbose=False):
        Sensor.__init__(self, pin, id, label, verbose)
        self.sensor_type_nb = parse_number(sensor_type, 22)
        self.pin = pin

        if self.sensor_type_nb == 11:
            sensor = Adafruit_DHT.DHT11
        elif self.sensor_type_nb == 2302:
            sensor = Adafruit_DHT.AM2302
        else :
            sensor = Adafruit_DHT.DHT22

        if self.verbose:
            print 'DBG: DHT{} sensor \'{}\' pin {}'.format(
                self.sensor_type_nb, label, pin)

        self.humidity, self.temperature = Adafruit_DHT.read_retry(sensor, pin)

        if self.verbose:
            print 'DBG: Temperature = {:.2f} °C'.format(self.temperature)
            print 'DBG: Humidity    = {:.2f} %'.format(self.humidity)

    def generate_id(self, param):
        return '{}_{}'.format(parse_number(param, default=0), DHT_STR)

    def type(self):
        return '{}{}'.format(DHT_STR, self.sensor_type_nb)

    def template_type(self):
         return TPL_TEMP_HUM

    def sensor_data_types(self):
        return ['temperature', 'humidity']

    def dictionary(self):
        return dict(
            type=self.type(),
            id=self.id,
            label=self.label,
            time=datetime.now().strftime(config.dt_format),
            temperature='{:.2f}'.format(self.temperature),
            temperatureUnit='C',
            humidity='{:.2f}'.format(self.humidity),
            humidityUnit='%')

    def csv_header(self):
        return 'Time;Temperature °C;Humidity %\n'

    def csv_line(self):
        return '{};{:.2f};{:.2}\n'.format(
            datetime.now().strftime(config.dt_format),
            self.temperature,
            self.humidity)