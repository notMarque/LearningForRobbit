### PIO Program to wait a certain amount of time, then push a value to the RX FIFO to trigger a DMA channel

### Python Bits needed
import rp2
from rp2 import PIO, StateMachine, asm_pio, DMA
import time
from machine import Pin

# Create a function that creates an integer bumber whose binary representation has the bits flipped at the indexes passed in a list of integers (assuming the bits are zero indexed)
def FlipBits(dmas):
    i = 0
    a = 0
    while i < len(dmas):
        a += pow(2, dmas[i])
        i += 1
    return a


@rp2.asm_pio(in_shiftdir=PIO.SHIFT_LEFT, out_shiftdir=PIO.SHIFT_RIGHT)
def pioquad():
    # Encoder Reader (Instructions 1-24)
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
    
    #### Setup For Timer Loop: (Instructions 25-26)
    # Start By Filling Y Register With number of Cycles to delay
    pull(block)
    mov(y, isr)
    # If it cannot simply go to next instruction (because of wrap), then could use a jmp() here to get into main loop

    ##### Main Loop For Timer: (Instructions 27-30)
    # Assuming that the countdown start value is already in the y-register
    # This will decrement through the counter, pushing a value(all-zeros) to the RX FIFO
    wrap_target() 

    jmp(x_dec, "COUNTER_CONT")  # Will skip all things of substance unless X scratch is zero, decrementing along the way
    push(noblock)               # Will push a value to the RX FIFO to trigger a DMA channel
    mov(x, y)                   # Reset the X scratch to the initial countdown value
    pull(noblock)               # Will pull a value from the TX FIFO to keep dma channel from stalling if it is putting data back here

    label("COUNTER_CONT")       # Jump to location that skips stuff of value
    wrap()                      # Wrap back to the jmp, saves a command
    
    # Nop to fill memory: (Instructions 31-32)
    # Since micropython doesn't offer a way to specify that it starts at the beginning of the instructions, the remaining instructions must be filled with nop()
    nop()
    nop()


PIO0_BASES = [0x50200000, 0x50300000]

sys_clk = 125_000_000 # I'm yet to find a way to access the actual clock speed

velocityTrackingPeriod = 5                                 # How often position values should be stored for performing velocity calculations (ms) (It is expected that 5-25 will be appropriate)
countdownNum = velocityTrackingPeriod / 1000*sys_clk -3   # (Period of velocity calculation)/(1000 ms in one second)*(sys_clk in Hz) - (3 commands that happen once every full countdown)


# Needed Later # StateMachine.put(countdownNum, shift=0) # Need to use this to put the countdown value into the TX FIFO

class PIOQuadEncoder:
    
    def __init__(self, encoderPins: list, positionMemory: bool):
        succeeded = True                        # Tracking for failures whil instantiating state machines
        
        # Read length of pins inputted to see how many encoders to create, if too many passed, only create first three
        numEncoders = int(len(encoderPins))     # Check how many pins were passed, this is how many state machines are asked for
        if numEncoders > 3:                     # If asking for more than 3 encoders, will only create the first 3
            succeeded = False
            numEncoders = 3
        numEncoders    
        
        self.stateMachines = list()             # Creates a list to store all stateMachine objects
        
        self.leftDmas = list()                  # Creates a list to store all DMA channels on the left side of the ping-pong
        self.rightDmas = list()                 # same for right side of ping pong
        
        self.positions = list()                 # Creates a list to store the bytearrays that the ticks are stored in in
        self.lastPositions = list()             # Creates a list to store past values of position
        self.lasterPositions = list()           # Creates a list to store more past values of position

        # Encoder Information
        self.TICKS_PER_REV = 700

        # Cycle through for each Quad Encoder creating necessary state machines and memory locations for each
        i = 0
        while(i < numEncoders):
            self.stateMachines.append(rp2.StateMachine(i, pioquad, in_base=Pin(encoderPins[i]))) # Create the state machine for tracking encoder i's position
            
            if not positionMemory: self.stateMachines[i].exec("mov(y, null)")                    # If not storing position from previous code execution, clear the Y register (position)
            
            self.stateMachines[i].active(1)             # Start state machine i running

            # Appending instances for updating position
            self.leftDmas.append(DMA())      # appending DMA object to list
            self.rightDmas.append(DMA())    # appending other DMAs to an equal sized list to create ping-pong
            self.positions.append(bytearray(4))      # append a bytearray of 4 bytes (32 bits) to the array of positions
            self.lastPositions.append(bytearray(4))      # Append bytearray for storing most recent past position
            self.lasterPositions.append(bytearray(4))    # Append bytearray for storing older positions

            ########## Initializing PIO Data Retrieval DMAs ############
            # pack values into a control register value
            # does not increment read, does not increment write, sets the transfer request to the appropriate PIO FIFO, sets bit reverse to true
            controlL = self.leftDmas[i].pack_ctrl(inc_read=False, inc_write=False, treq_sel=(4+i), bswap=True, chain_to=self.rightDmas[i].channel)
            controlR = self.rightDmas[i].pack_ctrl(inc_read=False, inc_write=False, treq_sel=(4+i), bswap=True, chain_to=self.leftDmas[i].channel)

            # Configure the DMA channels for retrieving data from PIOS
            # - Sets read location to be the PIO0_Base + 32 (offset to reach RXF0) + 8 for each subsequent state machine to reach its respective location
            # - Sets write location to the corresponding bytearray in the positions list
            # - Sets the count to 1; completes one transfer before the channel stops
            # - Passes the control register value that was packed before
            # - triggers the DMA to start passing data

            self.leftDmas[i].config(read=(PIO0_BASES[0]+32+i*4), write=self.positions[i], count=1, ctrl=controlL, trigger=True)
            self.rightDmas[i].config(read=(PIO0_BASES[0]+32+i*4), write=self.positions[i], count=1, ctrl=controlR, trigger=True)
            
            i += 1                          # increment for next encoder


        # DMAs that will monitor the timer statemachine
        self.leftTimerDMA = DMA()              # Creating DMA that will react to timer
        self.rightTimerDMA = DMA()             # Creating DMA that will react to timer
        
        controlLTimerDMA = self.leftTimerDMA.pack_ctrl(inc_read=False, inc_write=False, treq_sel=())

######## WORKING HERE######
        
        ############ Initializing Velocity Value DMAs #########
        # pack values into a control register
        # - Don't increment read or write
        # - Don't swap the bits!
        # - Chain the first one to the second
        controlTimed = self.timedDmas[i].pack_ctrl(inc_read=False, inc_write=False, treq_sel=(numEncoders), bswap=False, chain_to=self.chainedToDmas[i].channel)
        controlChained = self.chainedToDmas[i].pack_ctrl(inc_read=False, inc_write=False, bswap=False)

        # Configure the DMA channels for pulling off data for velocity readings
        self.timedDmas[i].config(read=self.lastPositions[i], write=self.lasterPositions[i], count=1, ctrl=controlTimed, trigger=True)
        self.chainedToDmas[i].config(read=self.positions[i], write=self.lastPositions[i], count=1, ctrl=controlChained, trigger=True)
