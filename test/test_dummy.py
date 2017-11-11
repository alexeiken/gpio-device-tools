# -*- coding: utf-8 -*-
import unittest
from gpio_device_tools import sensor


class TestDummySensor(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.s = sensor.DummySensor(label='Test')

    def test_properties(self):
        self.assertEqual('dummy', self.s.id)
        self.assertEqual('Test', self.s.label)
        self.assertEqual(False, self.s.verbose)

    def test_dictionary(self):
        dictionary = self.s.dictionary()

        self.assertEquals('dummy', dictionary['type'])
        self.assertEquals('dummy', dictionary['id'])
        self.assertEquals('Test', dictionary['label'])
        self.assertEquals('2016-08-02T22:27:49', dictionary['time'])
        self.assertEquals('20.12', dictionary['temperature'])
        self.assertEquals('C', dictionary['temperatureUnit'])

    def test_sensor_data(self):
        self.assertEquals(['temperature'], self.s.sensor_data_types())

    def test_csv_data(self):
        self.assertEquals('Time;Temperature °C\n', self.s.csv_header())
        self.assertEquals('2016-08-02T22:27:49;20.12\n', self.s.csv_line())

    def test_text_format(self):
        self.assertEqual('Label: Test\n'
                         'Time : 2016-08-02T22:27:49\n'
                         'Temperature: 20.12 \xc2\xb0C',
                         self.s.text_format())

    def test_xml_format(self):
        self.assertEqual('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                         '<sensor>\n'
                         '    <type>dummy</type>\n'
                         '    <id>dummy</id>\n'
                         '    <label>Test</label>\n'
                         '    <time>2016-08-02T22:27:49</time>\n'
                         '    <temperature unit="C">20.12</temperature>\n'
                         '</sensor>',
                         self.s.xml_format())

    def test_json_format(self):
        self.assertEqual('{\n'
                         '  "type": "dummy",\n'
                         '  "id": "dummy",\n'
                         '  "label": "Test",\n'
                         '  "time": "2016-08-02T22:27:49",\n'
                         '  "temperature": {\n'
                         '    "value": "20.12",\n'
                         '    "unit": "C"\n'
                         '  }\n'
                         '}',
                         self.s.json_format())


if __name__ == '__main__':
    unittest.main()