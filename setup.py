from setuptools import setup, find_packages
import io
import os
import sys


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        if os.path.isfile(filename):
            with io.open(filename, encoding=encoding) as f:
                buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt', 'CHANGES.txt')

setup(
    name='gpio-device-tools',
    version='0.4',
    author='Alexander Eiken',
    author_email='Alex@nder-Eiken.de',
    description='Tools for accessing sensors and binding devices connected to GPIO pins of credit card sized computers',
    long_description=long_description,
    license='Apache Software License',
    keywords = 'CHIP IO GPIO MQTT',
    url='',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Home Automation',
        'Topic :: System :: Hardware'
    ],

    packages=find_packages(),

    scripts = ['scripts/gpioread',
               'scripts/gpiowrite',
               'scripts/mqttgpiobind'],

    data_files=[('gpio_device_tools/templates/temp', ['gpio_device_tools/templates/temp/template.txt',
                                                      'gpio_device_tools/templates/temp/template.json',
                                                      'gpio_device_tools/templates/temp/template.xml']),
                ('gpio_device_tools/templates/temp_hum', ['gpio_device_tools/templates/temp_hum/template.txt',
                                                          'gpio_device_tools/templates/temp_hum/template.json',
                                                          'gpio_device_tools/templates/temp_hum/template.xml']),
                ('gpio_device_tools/templates/temp_pres_alt', ['gpio_device_tools/templates/temp_pres_alt/template.txt',
                                                               'gpio_device_tools/templates/temp_pres_alt/template.json',
                                                               'gpio_device_tools/templates/temp_pres_alt/template.xml'])],

    install_requires=[
        'paho-mqtt>=1.2',
        'Adafruit-GPIO>=1.0.1',
        'CHIP_IO>=0.2'
    ],

    tests_require=[
        'pytest'],

    extras_require={
        'testing': ['pytest'],
    },

    test_suite = 'tests'
)
