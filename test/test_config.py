# -*- coding: utf-8 -*-
import unittest
from gpio_device_tools import config
from gpio_device_tools.config import ConfigurationError


class TestSensorConfig(unittest.TestCase):

    def test_sensors1(self):
        self.cfg = config.SensorConfigReader("test/sensors1.cfg")
        self.assertEqual(2, len(self.cfg.sensors))

        self.assertEqual(2, self.cfg.sensors[0].out_channel)
        self.assertEqual('path/test.json', self.cfg.sensors[0].out_file)
        self.assertEqual(None, self.cfg.sensors[0].hostname)
        self.assertEqual(None, self.cfg.sensors[0].mqtt_cfg_file)
        self.assertEqual('ds1820', self.cfg.sensors[0].sensor_type)
        self.assertEqual('10-00080234149b', self.cfg.sensors[0].sensor_param)
        self.assertEqual('Temp-1', self.cfg.sensors[0].id)
        self.assertEqual('Temperature 1', self.cfg.sensors[0].label)
        self.assertEqual('/test/abc', self.cfg.sensors[0].topic)

        self.assertEqual(2, self.cfg.sensors[1].out_channel)
        self.assertEqual('path/test.json', self.cfg.sensors[1].out_file)
        self.assertEqual(None, self.cfg.sensors[1].hostname)
        self.assertEqual(None, self.cfg.sensors[1].mqtt_cfg_file)
        self.assertEqual('dummy', self.cfg.sensors[1].sensor_type)
        self.assertEqual(None, self.cfg.sensors[1].sensor_param)
        self.assertEqual('ID', self.cfg.sensors[1].id)
        self.assertEqual('Label', self.cfg.sensors[1].label)
        self.assertEqual(None, self.cfg.sensors[1].topic)

    def test_sensors2(self):
        self.cfg = config.SensorConfigReader("test/sensors2.cfg")
        self.assertEqual(2, len(self.cfg.sensors))

        self.assertEqual(4, self.cfg.sensors[0].out_channel)
        self.assertEqual(None, self.cfg.sensors[0].out_file)
        self.assertEqual('test', self.cfg.sensors[0].hostname)
        self.assertEqual('test/sensors2.cfg', self.cfg.sensors[0].mqtt_cfg_file)
        self.assertEqual('ds1820', self.cfg.sensors[0].sensor_type)
        self.assertEqual('10-00080234149b', self.cfg.sensors[0].sensor_param)
        self.assertEqual('Temp-1', self.cfg.sensors[0].id)
        self.assertEqual('Temperature 1', self.cfg.sensors[0].label)

        self.assertEqual(4, self.cfg.sensors[1].out_channel)
        self.assertEqual(None, self.cfg.sensors[1].out_file)
        self.assertEqual('test', self.cfg.sensors[1].hostname)
        self.assertEqual('test/sensors2.cfg', self.cfg.sensors[0].mqtt_cfg_file)
        self.assertEqual('dummy', self.cfg.sensors[1].sensor_type)
        self.assertEqual(None, self.cfg.sensors[1].sensor_param)
        self.assertEqual('ID', self.cfg.sensors[1].id)
        self.assertEqual('Label', self.cfg.sensors[1].label)

    def test_sensors_invalid1(self):
        with self.assertRaises(Exception) as context:
            config.SensorConfigReader("test/sensors_invalid1.cfg")

        self.assertEqual('Unsupported value \'illegal\' for option \'output\' in section [default]',
                         context.exception.value)

    def test_sensors_invalid2(self):
        with self.assertRaises(Exception) as context:
            config.SensorConfigReader("test/sensors_invalid2.cfg")

        self.assertEqual('Value \'hostname\' needs to be defined for MQTT output',
                         context.exception.value)

    def test_sensors_invalid3(self):
        with self.assertRaises(Exception) as context:
            config.SensorConfigReader("test/sensors_invalid3.cfg")

        self.assertEqual('Value \'file\' needs to be defined for CSV output',
                         context.exception.value)


class TestMqttBindingConfig(unittest.TestCase):

    def test_mqttd(self):
        self.cfg = config.MqttBindingConfigReader("test/mqttd.cfg")
        self.assertEqual(2, len(self.cfg.bindings))

        self.assertEqual('test/value', self.cfg.bindings[0].topic)
        self.assertEqual('XIO-P4', self.cfg.bindings[0].pin)
        self.assertEqual(True, self.cfg.bindings[0].invert)

        self.assertEqual('test/value2', self.cfg.bindings[1].topic)
        self.assertEqual('XIO-P5', self.cfg.bindings[1].pin)
        self.assertEqual(False, self.cfg.bindings[1].invert)

    def test_mqttd_invalid(self):
        with self.assertRaises(Exception) as context:
            config.MqttBindingConfigReader("test/mqttd_invalid.cfg")

        self.assertEqual('Value \'topic\' not defined in section [binding2]',
                         context.exception.value)


class TestMqttServerConfig(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cfg = config.MqttServerConfigReader("test/mqtt.cfg")

    def test_properties(self):
        self.assertEqual('test', self.cfg.mqtt_host)
        self.assertEqual('3333', self.cfg.port)
        self.assertEqual('gpio-device-tools', self.cfg.client_id)
        self.assertEqual(1, self.cfg.qos)
        self.assertEqual(True, self.cfg.retain)
        self.assertEqual(42, self.cfg.keepalive)


if __name__ == '__main__':
    unittest.main()