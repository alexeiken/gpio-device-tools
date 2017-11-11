# -*- coding: utf-8 -*-
import array
import fcntl
import io
import time
from datetime import datetime

import config
from sensor import Sensor, parse_number, TPL_TEMP_HUM

HTU21D_STR = 'htu21d'


class I2CSystem:

    _I2C_SLAVE = 0x0703

    def __init__(self, device, bus):
        self.fr = io.open('/dev/i2c-'+str(bus), 'rb', buffering=0)
        self.fw = io.open('/dev/i2c-'+str(bus), 'wb', buffering=0)

        fcntl.ioctl(self.fr, self._I2C_SLAVE, device)
        fcntl.ioctl(self.fw, self._I2C_SLAVE, device)

    def write(self, bytes):
        self.fw.write(bytes)

    def read(self, bytes):
        return self.fr.read(bytes)

    def close(self):
        self.fw.close()
        self.fr.close()


class HTU21Sensor(Sensor):

    # HTU21D-F Address
    __HTU21DF_I2CADDR = 0x40

    # HTU21D-F Commands
    __CMD_READ_TEMP_HOLD   = '\xE3'
    __CMD_READ_HUMI_HOLD   = '\xE5'
    __CMD_READ_TEMP_NOHOLD = '\xF3'
    __CMD_READ_HUMI_NOHOLD = '\xF5'
    __CMD_WRIT_USR_REG     = '\xE6'
    __CMD_READ_USR_REG     = '\xE7'
    __CMD_SOFT_RESET       = '\xFE'

    def __init__(self, param='0', id=None, label=HTU21D_STR, verbose=False):
        Sensor.__init__(self, param, id, label, verbose)

        bus_nb = parse_number(param, 0)

        if self.verbose:
            print 'DBG: HTU21D sensor \'{}\' bus number {:d}'.format(
                label, bus_nb)

        self.dev = None
        try:
            self.dev = I2CSystem(self.__HTU21DF_I2CADDR, bus_nb)

            self.__htu_reset()
            self.temperature = self.__read_temperature()

            self.__htu_reset()
            self.humidity = self.__read_humidity(self.temperature)
        finally:
            if self.dev is not None:
                self.dev.close()

    def __htu_reset(self):
        self.dev.write(self.__CMD_SOFT_RESET)
        time.sleep(.1)

    def __crc8check(self, value):
        # Ported from Sparkfun Arduino HTU21D Library: https://github.com/sparkfun/HTU21D_Breakout
        remainder = ((value[0] << 8) + value[1]) << 8
        remainder |= value[2]

        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1
        # divsor = 0x988000 is the 0x0131 polynomial shifted to farthest left of three bytes
        divisor = 0x988000

        for i in range(0, 16):
            if remainder & 1 << (23 - i):
                remainder ^= divisor
            divisor >>= 1

        if remainder == 0:
            return True
        else:
            return False

    def __read_temperature(self):
        if self.verbose:
            print 'DBG: Reading temperature'

        self.dev.write(self.__CMD_READ_TEMP_NOHOLD)
        time.sleep(.1)

        data = self.dev.read(3)
        buf = array.array('B', data)

        if self.verbose:
            print 'DBG: msb = {:d}'.format(buf[0])
            print 'DBG: lsb = {:d}'.format(buf[1])
            print 'DBG: crc = {:d}'.format(buf[2])

        if not self.__crc8check(buf):
            if self.verbose:
                print 'DBG: CRC check failed'
            return None

        temp_reading = (buf[0] << 8 | buf [1]) & 0xFFFC

        temperature = ((temp_reading / 65536.0) * 175.72 ) - 46.85

        if self.verbose:
            print 'DBG: Temperature = {:.2f} °C'.format(temperature)

        return temperature

    def __read_humidity(self, temperature):
        if self.verbose:
            print 'DBG: Reading humidity'

        self.dev.write(self.__CMD_READ_HUMI_NOHOLD)
        time.sleep(.1)

        data = self.dev.read(3)
        buf = array.array('B', data)

        if self.verbose:
            print 'DBG: msb = {:d}'.format(buf[0])
            print 'DBG: lsb = {:d}'.format(buf[1])
            print 'DBG: crc = {:d}'.format(buf[2])

        if self.__crc8check(buf):
            if self.verbose:
                print 'DBG: CRC check failed'
            # ignore CRC check failure here
            #return 0

        humid_reading = (buf[0] << 8 | buf [1]) & 0xFFFC

        uncomp_humidity = (125.0 * (humid_reading / 65536.0)) - 6.0

        if self.verbose:
            print 'DBG: Uncompensated humidity = {:.2f} % - temperature = {:.2f} °C'\
                .format(uncomp_humidity, temperature)

        humidity = ((25 - temperature) * -0.15) + uncomp_humidity

        if self.verbose:
            print 'DBG: Humidity = {:.2f} %'.format(humidity)

        return humidity

    def generate_id(self, param):
        return '{}_{}'.format(parse_number(param, default=0), HTU21D_STR)

    def type(self):
        return HTU21D_STR

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
        return '{};{:.2f};{:.2f}\n'.format(
            datetime.now().strftime(config.dt_format),
            self.temperature,
            self.humidity)