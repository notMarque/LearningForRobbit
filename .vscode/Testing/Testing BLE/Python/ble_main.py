# Import necessary modules
from machine import Pin
import time 
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import uctypes

# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()

# Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)

# Create a Pin object for the onboard LED, configure it as an output
led = Pin("LED", Pin.OUT)

# Initialize the LED state to 0 (off)
led_state = 0

def on_rx(v):
    print("RX", v)

sp.on_write(on_rx)

test_data = bytearray(4)

# PIO Addresses
PIO_BASES = [0x50200000, 0x50300000]        # Bases for PIO registers (Sec 3.7 Pg 367 in RP2040 Datasheet)
TXF0_ADDR = 0x010                           # Offset for PIO FIFO 0   (Sec 3.7 Pg 367)

# DMA Addresses
DMA_BASE = 0x50000000                       # Base for DMA registers (Sec 2.5.7 Pg 101)
CH0_AL2_READ_ADDR=0x028                     # Address of CH0 Alias 2 Read Address Register for DMA  (Sec 2.5.7 Pg 102)
CH0_AL3_READ_ADDR_TRIG = 0x03c              # Address of CH0 Alias 3 Read Address Register for DMA  (Sec 2.5.7 Pg 102)
CH0_READ_ADDR = 0X0                         # CH0 Read Address Register (Sec 2.5.7 Pg 101)
DMA_TRIG_CHANNEL_OFFSET = 0x040             # Distance between addresses for each state DMA instances in bytes (Sec 2.5.7 Pg 101-102)

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
posRegs = bytearray(36)  # Allocate 40 bytes for storing addresses
posRegsStruct = uctypes.struct(uctypes.addressof(posRegs), PosRegistersStruct)  # Fill the bytearray with the appropriate st wit
        

poses = bytearray(12)   # Allocate 12 bytes for storing positions
posStruct = uctypes.struct(uctypes.addressof(poses), PositionStruct)

# Filling posRegs
# Set Read positions as TX FIFOs from first 3 state machines (doesn't matter if we're using them or not, they just won't be acted on)
posRegsStruct.read1 = PIO_BASES[0] + TXF0_ADDR + 4*0
posRegsStruct.read2 = PIO_BASES[0] + TXF0_ADDR + 4*1
posRegsStruct.read3 = PIO_BASES[0] + TXF0_ADDR + 4*2
posRegsStruct.readReset = uctypes.addressof(posRegs) + 32
# Set Write positions as correct offsets in the positions ucstruct
posRegsStruct.write1 = uctypes.addressof(poses)
posRegsStruct.write2 = uctypes.addressof(poses) + 4
posRegsStruct.write3 = uctypes.addressof(poses) + 8
posRegsStruct.writeReset = DMA_BASE + CH0_READ_ADDR + DMA_TRIG_CHANNEL_OFFSET * 3 # Instead of using TRIG channel allias. Just use the og since it will be chained to anyways
# Set read position for restarting loop of commanderDMA
posRegsStruct.tableAddress = uctypes.addressof(posRegs)

i = 0
while True:
    if sp.is_connected():
        # Short burst of queued notifications.
        for _ in range(1):
            data = str(i)
            print("TX", data)
            sp.send(data)
            i += 1
    time.sleep_ms(1)

"""
# Define a callback function to handle received data
def on_rx(data):
    print("Data received: ", data)  # Print the received data
    global led_state  # Access the global variable led_state
    if data == b'toggle\r\n':  # Check if the received data is "toggle"
        led.value(not led_state)  # Toggle the LED state (on/off)
        led_state = 1 - led_state  # Update the LED state

# Start an infinite loop
while True:
    if sp.is_connected():  # Check if a BLE connection is established
        sp.on_write(on_rx)  # Set the callback function for data reception"""