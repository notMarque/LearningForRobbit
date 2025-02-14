# Class to track quadrature encoder tick counter with PIO
# The class then provides a method to read the tick counter when necessary
# It can detect ticks at up to sysclock/10 (s0 theoretically 12.5M ticks per second)
# Up to 4 encoders can be tracked with just one PIO 
import rp2
from rp2 import PIO, StateMachine, asm_pio, DMA
from machine import Pin, Timer
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

PIO0_BASES = [0x50200000, 0x50300000]
# RXFIFO_OFFSETS = [const(0x020), const(0x024), const(0x028), const(0x02c)] # Offsets for RXF0, RXF1, RXF2, RXF3 respectively

class PIOQuadEncoder:
    
    def __init__(self, encoderPins: list):
        self.usedSMs = int(len(encoderPins))    # Reads length of pins provided to determine how many state machines needed
        self.stateMachines = list()             # Creates a list to store all stateMachine objects
        
        self.leftDmas = list()                  # Creates a list to store all DMA channels on the left side of the ping-pong
        self.rightDmas = list()                 # same for right side of ping pong
        self.positions = list()                 # Creates a list to store the bytearrays that the ticks are stored in in

        # Encoder Information
        self.TICKS_PER_REV = 700

        # Velocity tracking info
        self.pos = [0, 0, 0, 0]
        self.lastPos = [0, 0, 0, 0]
        self.VELOCITY_CALC_PERIOD = 100

        self.velocityTimer = Timer(mode=Timer.PERIODIC, period=self.VELOCITY_CALC_PERIOD, callback=self.velocityTracker)

        i = 0
        while(i < self.usedSMs):
            self.stateMachines.append(rp2.StateMachine(i, pioquad, in_base=Pin(encoderPins[i])))
            self.stateMachines[i].exec("mov(y, null)")
            self.stateMachines[i].active(1)

            self.leftDmas.append(DMA())      # appending DMA object to list
            self.rightDmas.append(DMA())    # appending other DMAs to an equal sized list to create ping-pong
            self.positions.append(bytearray(4))      # append a bytearray of 4 bytes to the array of positions

            # pack values into a control register value
            # does not increment read, does not increment write, sets the transfer request to the appropriate PIO FIFO, sets bit reverse to true
            controlL = self.leftDmas[i].pack_ctrl(inc_read=False, inc_write=False, treq_sel=(4+i), bswap=True, chain_to=self.rightDmas[i].channel)
            controlR = self.rightDmas[i].pack_ctrl(inc_read=False, inc_write=False, treq_sel=(4+i), bswap=True, chain_to=self.leftDmas[i].channel)

            # Configure the DMA channel
            # - Sets read location to be the PIO0_Base + 32 (offset to reach RXF0) + 8 for each subsequent state machine to reach its respective location
            # - Sets write location to the corresponding bytearray in the positions list
            # - Sets the count to 1; completes one transfer before the channel stops
            # - Passes the control register value that was packed before
            # - triggers the DMA to start passing data

            self.leftDmas[i].config(read=(PIO0_BASES[0]+32+i*4), write=self.positions[i], count=1, ctrl=controlL, trigger=True)
            self.rightDmas[i].config(read=(PIO0_BASES[0]+32+i*4), write=self.positions[i], count=1, ctrl=controlR, trigger=True)
            i += 1                          # increment for next encoder
        
    def getRawData(self, num):
        return self.positions[num]

    def getTickPos(self, num):
        val = int.from_bytes(self.positions[num])           # read value from byte array
        if val > 0x7FFFFFFF:
            return -(0xFFFFFFFF-val)
        else:
            return val
        
    def velocityTracker(self, tim):
        i = 0
        while i < self.usedSMs:
            self.lastPos[i] = self.pos[i]
            self.pos[i] = self.getTickPos(i)
            i += 1

    def getTickVelocity(self, id):
        return (600*(self.pos[id] - self.lastPos[id]))/float(self.TICKS_PER_REV)
    
    def stopEncoders(self):
        i = 0
        while i < self.usedSMs:
            self.leftDmas[i].close()
            self.rightDmas[i].close()
            i += 1
