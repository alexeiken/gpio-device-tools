# -*- coding: utf-8 -*-
import os
import unittest
from gpio_device_tools import ds1820


class TestSensorDS1820(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.s = ds1820.DS1820Sensor(
            sens_dir=os.path.dirname(__file__) ,
            sens_id='10-00080234149b',
            id='abc', label='Test', verbose=True)

    def test_properties(self):
        self.assertEqual('abc', self.s.id)
        self.assertEqual('Test', self.s.label)
        self.assertEqual(True, self.s.verbose)

    def test_dictionary(self):
        dictionary = self.s.dictionary()

        self.assertEquals('ds1820', dictionary['type'])
        self.assertEquals('abc', dictionary['id'])
        self.assertEquals('Test', dictionary['label'])
        self.assertIsNotNone(dictionary['time'])
        self.assertEquals('27.31', dictionary['temperature'])
        self.assertEquals('C',dictionary['temperatureUnit'])

    def test_sensor_data(self):
        self.assertEquals(['temperature'], self.s.sensor_data_types())

    def test_csv_header(self):
        self.assertEquals('Time;Temperature °C\n', self.s.csv_header())

if __name__ == '__main__':
    unittest.main()