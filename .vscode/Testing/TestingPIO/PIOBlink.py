import time
import rp2
from machine import Pin

# Define the blink program. It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blink visible\
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)

def blink():
    wrap_target()
    set(pins, 1)    [31]
    nop()           [31]
    nop()           [31]
    nop()           [31]
    nop()           [31]
    set(pins, 0)    [31]
    nop()           [31]
    nop()           [31]
    nop()           [31]
    nop()           [31]
    wrap()

# Instantiate a state machine at 2000Hz, with set bound to pin 25(the onboard led)
sm = rp2.StateMachine(0, blink, freq=2000, set_base=Pin(25))

# Run the state machine for 3 seconds
sm.active(1)
time.sleep(3)
sm.active(0)