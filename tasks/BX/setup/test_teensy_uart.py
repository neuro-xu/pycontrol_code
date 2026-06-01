# Test UART communication between pyboard and a Teensy

from pyControl.utility import *
from hardware_definition import *

# Define hardware (normally done in seperate hardware definition file).
uart = UART(board.port_4.UART, 115200)
uart.init(115200, bits=8, parity=None, stop=1)
state_duration = 5

# States and events.

states = [
    "UART_on",
    "UART_off",
]

events = ["teensy_sync"]

initial_state = "UART_off"

# State behaviour functions
def run_start():
    uart.write(b'0:B\n')


def UART_on(event):
    if event == "entry":
        uart.write(b'0:S70\n')
        timed_goto_state("UART_off", state_duration * second)
 
    elif event == "exit":
        pass


def UART_off(event):
    if event == "entry":
        uart.write(b'0:S30\n')
        timed_goto_state("UART_on", state_duration * second)


# Run end behaviour


def run_end():  # Turn off hardware at end of run.
    uart.write(b'C\n')
    uart.deinit()
