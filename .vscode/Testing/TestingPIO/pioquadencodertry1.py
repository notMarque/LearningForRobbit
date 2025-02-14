# Class to track quadrature encoder tick counter with PIO
# The class then provides a method to read the tick counter when necessary
# It can detect ticks at up to sysclock/10 (s0 theoretically 12.5M ticks per second)
# Up to 4 encoders can be tracked with just one PIO 

from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import time

@rp2.asm_pio(in_shiftdir=PIO.SHIFT_LEFT, out_shiftdir=PIO.SHIFT_RIGHT)

def pioquad():
    # 00 previous state
    jmp("UPDATE")       # current state 00
    jmp("DECREMENT")    # current state 01
    jmp("INCREMENT")    # current state 10
    jmp("UPDATE")       # current state 11

    # 01 previous state
    jmp("INCREMENT")    # current state 00
    jmp("UPDATE")       # current state 01
    jmp("UPDATE")       # current state 10
    jmp("DECREMENT")    # current state 11

    # 10 previous state
    jmp("DECREMENT")    # current state 00
    jmp("UPDATE")       # current state 01
    jmp("UPDATE")       # current state 10
    jmp("INCREMENT")    # current state 11

    # 11 previous state (to reduce size the last two states are implemented in place and become the target for the other jumps)
    jmp("UPDATE")       # current state 00
    jmp("INCREMENT")    # current state 01

    # The following y_dec and x_dec jumps are pointed to the next address so that they act as pure decrements regardless of condition
    label("DECREMENT")
    jmp(y_dec, "UPDATE")# current state 10 / jumped to from other state

    wrap_target()       # main loop starts here

    # copy position (which is stored in shift y) into isr and push it to the FIFO (nonblocking)
    label("UPDATE")     
    mov(isr, y)         # current state 11 / jumped to from other state
    push(noblock)   

    # shift the last state of the 2 input pins to the ISR (from the OSR) and shift in the new state of the pins
    # this produces the 4 bit target for the computed jump into the correct action for this state
    # both the `push` above and `out` below zero out the other bits in ISR
    label("SAMPLE_PINS")
    out(isr, 2)
    in_(pins, 2)

    mov(osr, isr)       # save state in the osr so we can use the ISR for other purposes
    mov(pc, isr)        # jump to the correct state machine action

    # the PIO does not have an increment instruction, so to do the same, we do a negate, decrement, negate sequence
    label("INCREMENT")
    mov(y, invert(y))   # negate y
    jmp(y_dec, "INCREMENT_CONT")    # another jump to next line to allow for just a decrement
    label("INCREMENT_CONT")
    mov(y, invert(y))

    wrap()              # wrap instead of jump saves 1 instruction

    # The preceeding code takes 24 operations
    # Since micropython doesn't offer a way to specify that it starts at the beginning of the instructions, the remaining instructions must be filled with nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    nop()
    
# Instantiarte a state machine at X Hz
sm = rp2.StateMachine(0, pioquad, in_base=Pin(18))

sm.active(1)

def read():
    n = sm.rx_fifo()
    for n in range(n):
        sm.get()

    val = sm.get()
    if val > 0x7FFFFFFF:
        return -(0xFFFFFFFF-val)
    else:
        return val 

while True:
    try:
        print(read())
        time.sleep_ms(10)
    except KeyboardInterrupt:
        print("Ended by Keyboard Interrupt")
        break