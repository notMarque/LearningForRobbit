### Goal of this file is to convert transfer the data from the PIO FIFOs to memory with a single pair of DMAs with a control block

### Python Bits needed
import rp2
from rp2 import PIO, StateMachine, asm_pio, DMA
import time
from machine import Pin
import uctypes


# PIO Addresses
PIO_BASES = [0x50200000, 0x50300000]        # Bases for PIO registers (Sec 3.7 Pg 367 in RP2040 Datasheet)
TXF0_ADDR = 0x020                           # Offset for PIO FIFO 0   (Sec 3.7 Pg 367) 
####### Try 0x020 above ###########################

# DMA Addresses
DMA_BASE = 0x50000000                       # Base for DMA registers (Sec 2.5.7 Pg 101)
CH0_AL2_READ_ADDR=0x028                     # Address of CH0 Alias 2 Read Address Register for DMA  (Sec 2.5.7 Pg 102)
CH0_AL3_READ_ADDR_TRIG = 0x03c              # Address of CH0 Alias 3 Read Address Register for DMA  (Sec 2.5.7 Pg 102)
CH0_READ_ADDR = 0X0                         # CH0 Read Address Register (Sec 2.5.7 Pg 101)
DMA_CHANNEL_OFFSET = 0x040             # Distance between addresses for each state DMA instances in bytes (Sec 2.5.7 Pg 101-102)
TIMER0_TREQ = 0x3b                          # TREQ Number for Timer 0 (Sec 2.5.7 Pg 112)
TIMER0_X_Y = 0x420                          # Fractional Divider Register for timer 0 (Sec 2.5 Pg 108)



## Uctypes struct for storing read and write addresses
PosRegistersStruct = {
    "read1": 0 | uctypes.INT32,
    "write1": 4 | uctypes.INT32,
    "read2": 8 | uctypes.INT32,
    "write2": 12 | uctypes.INT32,
    "read3": 16 | uctypes.INT32,
    "write3": 20 | uctypes.INT32,
    "readReset": 24 | uctypes.INT32,
    "writeReset": 28 | uctypes.INT32,
    "tableAddress": 32 | uctypes.INT32
}

## Uctypes struct for storing position values
PositionStruct = {
    "pos0": 0 | uctypes.INT32,
    "pos1": 4 | uctypes.INT32,
    "pos2": 8 | uctypes.INT32
}

## Uctypes struct for setting DMA clock divider
TimerStruct = {
    "y": 0 | uctypes.INT16,
    "x": 2 | uctypes.INT16
}
timer0ratioStruct = uctypes.struct(TIMER0_X_Y, TimerStruct)
timer0ratioStruct.y = 20000
timer0ratioStruct.x = 1


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

    # 11 previous state (to reduce size the last two states are implemented in place and become the target for t becther jumps)
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

    mov(osr, isr)       # save state in the osr so we can usein t ISR for other purposes
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

class PIOQuadEncoder:
    
    def __init__(self, encoderPins: list, ticks: int, positionMemory: bool):
        # Encoder Information
        self.TICKS_PER_REV = ticks
        
        ### Creating ustruct to use as a control block for the controller DMA 
        self.posRegs = bytearray(36)  # Allocate 36 bytes for storing addresses
        self.posRegsStruct = uctypes.struct(uctypes.addressof(self.posRegs), PosRegistersStruct)  # Treat the bytearray as the appropriate struct
        
        ## Creating ustruct to store position values in
        self.positions = bytearray(12)   # Allocate 12 bytes for storing positions
        self.posStruct = uctypes.struct(uctypes.addressof(self.positions), PositionStruct)  # Treat the bytearray as the appropriate struct

        self.commanderDMA = DMA()               # Creates a DMA that will reprogram the other dma
        self.followerDMA = DMA()                # Creates a DMA that will make the transfers

        # Filling posRegs
        # Set Read positions as TX FIFOs from first 3 state machines (doesn't matter if we're using them or not, they just won't be acted on)
        self.posRegsStruct.read1 = PIO_BASES[0] + TXF0_ADDR + 4*0   # Take the PIO base and add the TX FIFO Address plus an offset of 4 bytes per channel
        self.posRegsStruct.read2 = PIO_BASES[0] + TXF0_ADDR + 4*1
        self.posRegsStruct.read3 = PIO_BASES[0] + TXF0_ADDR + 4*2
        self.posRegsStruct.readReset = uctypes.addressof(self.posRegs) + 32
        # Set Write positions as correct offsets in the positions ucstruct
        self.posRegsStruct.write1 = uctypes.addressof(self.positions)
        self.posRegsStruct.write2 = uctypes.addressof(self.positions) + 4
        self.posRegsStruct.write3 = uctypes.addressof(self.positions) + 8
        self.posRegsStruct.writeReset = DMA_BASE + CH0_READ_ADDR + DMA_CHANNEL_OFFSET * self.commanderDMA.channel # Write to notmal Read Address as opposed to a trigger alias because it will be chained to anyway
        # Set read position for restarting loop of commanderDMA
        self.posRegsStruct.tableAddress = uctypes.addressof(self.posRegs)

        succeeded = True                        # Tracking for failures while instantiating state machines
        # Read length of pins inputted to see how many encoders to create, if too many passed, only create first three
        numEncoders = int(len(encoderPins))     # Check how many pins were passed, this is how many state machines are asked for
        if numEncoders > 3:                     # If asking for more than 3 encoders, will only create the first 3
            succeeded = False
            numEncoders = 3
        # numEncoders # This was just here and I don't know why
        
        self.stateMachines = list()             # Creates a list to store all stateMachine objects

        # Cycle through for each Quad Encoder creating necessary state machines and memory locations for each
        i = 0
        while(i < numEncoders):
            self.stateMachines.append(rp2.StateMachine(i, pioquad, in_base=Pin(encoderPins[i]))) # Create the state machine for tracking encoder i's position
            
            if not positionMemory: self.stateMachines[i].exec("mov(y, null)")                    # If not storing position from previous code execution, clear the Y register (position)
            
            self.stateMachines[i].active(1)             # Start state machine i running
            i += 1                          # increment for next encoder
        
        
        ########## Initializing PIO Data Retrieval DMAs ############
        # pack values into a control register value
        
        # Commander:
        # - Increments after both read and write
        # - sets bit reverse to false(kind of an assumption, but seems reasonable)
        # - has a ring size of 1 << 3 bites on the write, so it effectively alternates between writing to the read and write registers of the follower DMA
        # - Ring select is true to loop on write destination
        # - Chain to the follower DMA
        # - Use Timer0 as a transfer request to make sure that the dma is not outpacing the state machines(should adjust follower TREQ for each transfer in future, but this should at least get it going) 
        controlCmd = self.commanderDMA.pack_ctrl(inc_read=True, inc_write=True, treq_sel=TIMER0_TREQ, bswap=False, ring_size=3, ring_sel=True, chain_to=self.followerDMA.channel) # chain_to=self.followerDMA.channel,  took this out because it should already be being triggered
        
        # Follower:
        # - Don't increment or decrement because read and write values will be reset anyway
        # - Do bit swap values in order to get them the right way around for when resetting the commander DMA
        # - Chain to the commander to reconfigure
        controlFollower = self.followerDMA.pack_ctrl(inc_read=False, inc_write=False, bswap=False, chain_to=self.commanderDMA.channel)

        # Configure the channels

        # Follower:
        # - Read: doesn't matter as it will be reset by commander (known safe positmandis last value in posRegs)
        # - Write: also doesn't matter
        # - count is 1 because it will be transfering one word from each FIFO
        # - Don't trigger yet, as the commander needs to be triggered first
        self.followerDMA.config(count=1, ctrl=controlFollower, trigger=False)

        # Commander:
        # - Read from start of address list
        # - Write to READ_ADDR of follower so it assigns the write then read of the follower then chains to it
        # - Count is 2, one transfer for read address, one for write address
        self.commanderDMA.config(read=(self.posRegsStruct.tableAddress), write=(DMA_BASE + CH0_READ_ADDR + DMA_CHANNEL_OFFSET * self.followerDMA.channel), count=2, ctrl=controlCmd, trigger=True)


    def getRawData(self, num):
        #return self.stateMachines[num].tx_fifo()
        return self.followerDMA.active()
        """if (num == 0):
            return self.posStruct.pos0
        elif (num == 1):
            return self.posStruct.pos1
        else:
            return self.posStruct.pos2"""

    
    def stopEncoders(self):
        self.commanderDMA.close()
        self.followerDMA.close()
