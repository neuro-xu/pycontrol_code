# This hardware definition specifies that 3 pokes are plugged into ports 1-3 and a speaker into
# port 4 of breakout board version 1.2.  The houselight is plugged into the center pokes solenoid socket.

from devices import *

board = Breakout_1_2()

# Instantiate Devices.
left_poke = Poke(board.port_1, rising_event="left_poke", falling_event="left_poke_out")
center_poke = Poke(board.port_2, rising_event="center_poke", falling_event="center_poke_out")
right_poke = Poke(board.port_3, rising_event="right_poke", falling_event="right_poke_out")

teensy_sync = Frame_logger(pin=board.port_4.DIO_C, rising_event="teensy_sync")

hygrostat = Hygrostat(port=board.port_4, baudrate=115200)

# convert reward amount (uL) to time (ms)
# calibrated via solenoid_calibration.py
# reward_msPer5uL = [23, 25] # Rig 2
reward_msPer5uL = [26, 23] # Rig 1
# reward_msPer5uL = [25, 27] # Rig 3

# for compatibility
left_port = left_poke
right_port = right_poke
center_port = center_poke
final_valve = center_poke.SOL
