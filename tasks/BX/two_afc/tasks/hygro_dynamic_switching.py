# dynamically switch humidity set point between 30 and 70% every t seconds. Min settling time is 5 s.

from devices.hygrostat import Hygrostat
import pyControl.utility as pc
from hardware_definition import teensy_sync, board

pc.v.session_duration = 0.5 * pc.hour
pc.v.state_duration = 10 * pc.second
pc.v.default_flowrate = 1000 # mL/min
pc.v.left_cond = 0
pc.v.right_cond = 0

# States and events
conds = [-1, 0, 1] # -1: off, 0: low, 1: high
drawer = pc.drawer(repetitions=1, left_cond=conds, right_cond=conds)

events = ["teensy_sync", "new_condition", "session_timer"]
states = ["task_on"]
initial_state = "task_on"

hygrostat_left = Hygrostat(port=board.port_4, baudrate=115200, ID=0)
hygrostat_right = Hygrostat(port=board.port_4, baudrate=115200, ID=1)

def set_condition():
    sample = drawer.draw()
    pc.v.left_cond = sample["left_cond"]
    pc.v.right_cond = sample["right_cond"]
    if pc.v.left_cond == -1:
        hygrostat_left.set_humidity(0)
        hygrostat_left.set_flowrate(0)
    elif pc.v.left_cond == 0:
        hygrostat_left.set_humidity(30)
        hygrostat_left.set_flowrate(pc.v.default_flowrate)
    elif pc.v.left_cond == 1:
        hygrostat_left.set_humidity(70)
        hygrostat_left.set_flowrate(pc.v.default_flowrate)

    if pc.v.right_cond == -1:
        hygrostat_right.set_humidity(0)
        hygrostat_right.set_flowrate(0)
    elif pc.v.right_cond == 0:
        hygrostat_right.set_humidity(30)
        hygrostat_right.set_flowrate(pc.v.default_flowrate)
    elif pc.v.right_cond == 1:
        hygrostat_right.set_humidity(70)
        hygrostat_right.set_flowrate(pc.v.default_flowrate)

# State behaviour functions
def run_start():
    pc.set_timer("session_timer", pc.v.session_duration)
    hygrostat_left.begin()
    hygrostat_right.begin()

    pc.publish_event("new_condition")

def all_states(event):
    if event == "session_timer":
        pc.stop_framework()
    if event == "new_condition":
        set_condition()
        pc.print_variables(["right_cond", "left_cond"])
        pc.set_timer("new_condition", pc.v.state_duration + 2 * (pc.random() - 0.5) * pc.second) # jitter ±1 s


# Run end behaviour
def run_end():  # Turn off hardware at end of run.
    hygrostat_left.off()
    hygrostat_right.off()
