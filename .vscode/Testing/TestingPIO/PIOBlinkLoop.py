import time
import rp2
from machine import Pin

# Define the blink program. It has one GPIO to bind to on the set instruction, which is an output pin.
# Use lots of delays to make the blink visible\
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)

def blink():
    wrap_target()
    set(x, 31)  .side(1)    [6]             # set counter to 32 and set pin high
    label("HIGH_LOOP")                      
    jmp(x_dec, "HIGH_LOOP") .side(1) [15]   # cycle through loop, waiting cycles each time
    set(x, 31) .side(0)     [6]             # set pin low and set timer counter
    label("LOW_LOOP")
    jmp(x_dec, "LOW_LOOP") .side(0) [15]    # decrement through counter
    wrap()
    # Note that all commands must have .side() for EXECCTRL_SIDE_EN to be set to False. (asm_pio doesn't allow you to manually set it)

# Instantiate a state machine at 2000Hz, with sideset bound to pin 25(the onboard led)
sm = rp2.StateMachine(0, blink, freq=2000, sideset_base=Pin(25))

# Run the state machine for 3 seconds
sm.active(1)
time.sleep(3)
sm.active(0)