
import RPi.GPIO as gpio
from time import sleep
import logging

_logger = logging.getLogger('relayctrl')

_GPIO_RELAY_DIR_A = 8
_GPIO_RELAY_DIR_B = 10

_GPIO_RELAY_SEL_A = 3
_GPIO_RELAY_SEL_B = 5
_GPIO_RELAY_SEL_C = 7

_RELAY_SEL_MAP = [ \
    _GPIO_RELAY_SEL_A, \
    _GPIO_RELAY_SEL_B, \
    _GPIO_RELAY_SEL_C, \
]

_SWITCH_DELAY = 0.010

def initialize():
    _logger.info('Initialize')
    gpio.setmode(gpio.BOARD)
    gpio.setup([_GPIO_RELAY_DIR_A, \
                _GPIO_RELAY_DIR_B, \
                _GPIO_RELAY_SEL_A, \
                _GPIO_RELAY_SEL_B, \
                _GPIO_RELAY_SEL_C], \
               gpio.OUT)

def _relay_select(n):
    if n < 1 or n > 6 or not n:
        n = 8
    n -= 1
    pins = format(n, '03b')

    gpio.output([_GPIO_RELAY_SEL_A, \
                 _GPIO_RELAY_SEL_B, \
                 _GPIO_RELAY_SEL_C], gpio.HIGH)

    set_low = filter(lambda pin: pin, \
              map(lambda state, pin: state == '0' and pin, \
                  pins, _RELAY_SEL_MAP))

    gpio.output(set_low, gpio.LOW)

def _relay_close():
    gpio.output(_GPIO_RELAY_DIR_A, gpio.LOW)
    gpio.output(_GPIO_RELAY_DIR_B, gpio.HIGH)
def _relay_open():
    gpio.output(_GPIO_RELAY_DIR_A, gpio.HIGH)
    gpio.output(_GPIO_RELAY_DIR_B, gpio.LOW)
def _relay_neutral():
    gpio.output(_GPIO_RELAY_DIR_A, gpio.LOW)
    gpio.output(_GPIO_RELAY_DIR_B, gpio.LOW)

def set_relay(n, state):
    _logger.info('Set relay ' + str(n) + ': ' + str(state))
    _relay_neutral()
    _relay_select(n)
    if state:
        _relay_close()
    else:
        _relay_open()
    sleep(_SWITCH_DELAY)
    _relay_neutral()
    _relay_select(None)

def set_relays(relays, state):
    _logger.info('Set relays ' + str(relays) + ': ' + str(state))
    _relay_neutral()
    _relay_select(None)
    if state:
        _relay_close()
    else:
        _relay_open()
    for n in relays:
        _relay_select(n)
        sleep(_SWITCH_DELAY)
    _relay_neutral()
    _relay_select(None)

