from pyControl.hardware import Digital_input, Digital_output


class HeadfixedLickometer:
    # Two lick detectors and two solenoids.
    def __init__(
        self,
        port,
        rising_event_L="lick_l",
        falling_event_L="lick_l_off",
        rising_event_R="lick_r",
        falling_event_R="lick_r_off",
        debounce=5,
    ):
        self.lick_l = Digital_input(port.DIO_A, rising_event_L, falling_event_L, debounce)
        self.lick_r = Digital_input(port.DIO_B, rising_event_R, falling_event_R, debounce)
        self.SOL_R = Digital_output(port.POW_A)
        self.SOL_CTR = Digital_output(port.POW_B)
        self.SOL_L = Digital_output(port.POW_C)
