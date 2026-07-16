# A script for calibrating solenoids, derived from hardware_test.py in the examples.
import pyControl.utility as pc
from hardware_definition import lickometer

# States and events.

states = [
    "close_solenoids",
    "open_solenoids"
]

events = [
    "lick_l",
    "lick_r",
    "lick_l_off",
    "lick_r_off",
]

initial_state = "close_solenoids"

# Run start and stop behaviour.


def run_start():
    pass

def run_end():
    pass


# State behaviour functions.
def all_states(event):
    if event == "lick_l":
        pc.goto_state("open_solenoids")
    elif event == "lick_r":
        pc.goto_state("open_solenoids")
    elif event == "lick_l_off":
        pc.goto_state("close_solenoids")
    elif event == "lick_r_off":
        pc.goto_state("close_solenoids")

def open_solenoids(event):
    if event == "entry":
        lickometer.SOL_R.on()
        lickometer.SOL_L.on()
        lickometer.SOL_CTR.off()

def close_solenoids(event):
    if event == "entry":
        lickometer.SOL_R.off()
        lickometer.SOL_L.off()
        lickometer.SOL_CTR.on()