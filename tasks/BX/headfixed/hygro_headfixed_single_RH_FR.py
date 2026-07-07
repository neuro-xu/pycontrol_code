# dynamically switch humidity set point between 30 and 70% every t seconds. Min settling time is 5 s.

# from devices.hygrostat import Hygrostat
import pyControl.utility as pc
from hardware_definition import teensy_sync, board, hygrostat

pc.v.session_duration = 1.1 * pc.hour
pc.v.state_duration = 10 * pc.second
pc.v.default_flowrate = 1000 # mL/min
pc.v.RH = 30
pc.v.FR = 1000

# States and events
RH_lvls = [30, 40, 50, 60, 70]
FR_lvls = [1000]
drawer = pc.drawer(repetitions=1, RH=RH_lvls, FR=FR_lvls)

events = ["teensy_sync", "new_condition", "session_timer"]
states = ["task_on"]
initial_state = "task_on"

# hygrostat = Hygrostat(port=board.port_4, baudrate=115200, ID=3)

def set_condition():
    sample = drawer.draw()
    pc.v.RH = sample["RH"]
    pc.v.FR = sample["FR"]

    hygrostat.set_humidity(pc.v.RH)
    hygrostat.set_flowrate(pc.v.FR)

# State behaviour functions
def run_start():
    pc.set_timer("session_timer", pc.v.session_duration)
    hygrostat.begin()

    pc.publish_event("new_condition")

def all_states(event):
    if event == "session_timer":
        pc.stop_framework()
    if event == "new_condition":
        set_condition()
        pc.print_variables(["RH", "FR"])
        pc.set_timer("new_condition", pc.v.state_duration + 2 * (pc.random() - 0.5) * pc.second) # jitter ±1 s


# Run end behaviour
def run_end():  # Turn off hardware at end of run.
    hygrostat.off()
