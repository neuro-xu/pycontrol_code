from pyb import UART
from pyControl.hardware import Port

class Hygrostat:
    def __init__(self, port: Port, baudrate: int = 115200, ID=None):
        """Initialize the UART connection to the Teensy."""
        self.port = port
        self.baudrate = baudrate
        self.ID = ID
        self.uart = UART(port.UART, baudrate)
        self.RH_setpoint = None
        self.flow_rate = None
        self.begin()

    # ---------------------------
    # Low-level send methods
    # ---------------------------

    def send(self, cmd: str):
        """Send a command with no parameters."""
        if self.ID is not None:
            msg = f"{self.ID}:{cmd}\n".encode()
        else:
            msg = f"{cmd}\n".encode()
        
        self.uart.write(msg)

    def send1(self, cmd: str, arg1: int):
        """Send a command with one integer argument."""
        if self.ID is not None:
            msg = f"{self.ID}:{cmd}{arg1}\n".encode()
        else:
            msg = f"{cmd}{arg1}\n".encode() 
        
        self.uart.write(msg)

    def send2(self, cmd: str, arg1: int, arg2: int):
        """Send a command with two integer arguments."""
        if self.ID is not None:
            msg = f"{self.ID}:{cmd}{arg1}{arg2}\n".encode()
        else:
            msg = f"{cmd}{arg1}{arg2}\n".encode()
        
        self.uart.write(msg)

    # ---------------------------
    # High-level helpers
    # ---------------------------

    def set_humidity(self, RH_sp: int):
        """Set humidity setpoint."""
        self.send1("S", RH_sp)
        self.RH_setpoint = RH_sp

    def begin(self):
        """Begin/reset hygrostat"""
        self.uart.init(self.baudrate, bits=8, parity=None, stop=1)
        self.send("B")
        self.RH_setpoint = None
        self.flow_rate = None
    
    def tune(self):
        """Auto tune hygrostat"""
        self.send("T")

    def set_flowrate(self, flow: int):
        """Set flow rate (mL/min)"""
        self.send1("F", flow)
        self.flow_rate = flow

    def off(self):
        """Turning off stuff"""
        self.set_flowrate(0)
        self.send("C")
        self.uart.deinit()
        