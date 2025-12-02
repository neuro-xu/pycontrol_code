# Test UART communication between pyboard and a Teensy

from pyControl.utility import *
from hardware_definition import *

# Define hardware (normally done in seperate hardware definition file).
uart = UART(teensy_port.UART, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

# States and events.

states = [
    "UART_on",
    "UART_off",
]

events = []

initial_state = "UART_off"

# State behaviour functions


def UART_on(event):
    if event == "entry":
        uart.write(b'Hello\r\n')
        timed_goto_state("UART_off", 0.1 * second)
 
    elif event == "exit":
        pass


def UART_off(event):
    if event == "entry":
        timed_goto_state("UART_on", 0.1 * second)


# Run end behaviour


def run_end():  # Turn off hardware at end of run.
    uart.deinit()
