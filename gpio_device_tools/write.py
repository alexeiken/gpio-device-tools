#!/usr/bin/python
import sys
from optparse import OptionParser

import config


def main(argv):
    options = parse_options(argv)
    gpio_write(pin=options.pin[0], value=options.pin[1],
               verbose=options.verbose)


def parse_options(argv):
    usage = '\n' \
            '  gpiowrite --pin <ID> <value> [--verbose]\n' \
            '  gpiowrite -h | --help'

    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--pin',
                      dest='pin', nargs=2, metavar='<ID> <value>',
                      help='ID of the GPIO pin and value to be written to the pin: HIGH/LOW or true/false or 1/0')
    parser.add_option('-v', '--verbose',
                      action='store_true', dest='verbose', default=False,
                      help='enables verbose mode')
    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.error('Unsupported arguments: ' + ', '.join(args))

    if options.pin is None:
        parser.error('The option --pin with the arguments ID and value is not defined')

    if options.verbose:
        print 'DBG: Options= ', options

    return options


def gpio_write(pin, value, verbose=False):
    if config.chip_platform:
        if verbose:
            print "DBG: CHIP platform detected"
        v = str_2_one_zero(value)

        import CHIP_IO.GPIO as GPIO
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, v)
        GPIO.cleanup()

        if verbose:
            print "DBG: {} written to PIN {}".format(v, pin)
    else:
        v = config.get_boolean_value(value)

        import Adafruit_GPIO.GPIO as GPIO
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, v)
        GPIO.cleanup()

        if verbose:
            print "DBG: {} written to PIN {}".format(v, pin)


def str_2_one_zero(value):
    if config.get_boolean_value(value):
        return 1
    else:
        return 0

if __name__ == '__main__':
    main(sys.argv[1:])
