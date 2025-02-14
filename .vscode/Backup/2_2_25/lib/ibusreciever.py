# uart ibus test with micropython in pico
# works with flysky fs-i6x transmitter
# fs-rx2a pro receiver
# ibus protocol 32 bytes sent UART 115200 baud 8n1
# channel value range are 1000 - 2000 (1500 middle, good for servo)
#
# replace _lt_ with less than sign, youtube don't like angle brackets
#
#   0x20 0x40 - header
#   0xDC 0x05 - 1500 value (little endian 0x05 0xDC) channel 1
#   0xXX 0xXX - channel 2
#   0xXX 0xXX - channel 3
#   0xXX 0xXX - channel 4
#   0xXX 0xXX - channel 5
#   0xXX 0xXX - channel 6
#   0xXX 0xXX - channel 7
#   0xXX 0xXX - channel 8
#   0xXX 0xXX - channel 9
#   0xXX 0xXX - channel 10
#   0xXX 0xXX - channel 11
#   0xXX 0xXX - channel 12
#   0xXX 0xXX - channel 13
#   0xXX 0xXX - channel 14
#   0xXX 0xXX - checksum 0xFFFF minus sum of all above bytes (not including this checksum)
#
#   checksum above are also little endian

from machine import UART, Pin
#from typing import List, Union



def normal(v, mn,mx):
    return ((v-mn)/(mx-mn))
def mapFromNormalized(v, mn,mx):
    return v*(mx-mn)+mn


# An implementation of the i-Bus protocol for FlySky i6 transmitter/receiver
class IBusReceiver:
    results=[]
    __header = b' @'

    #Create an IBus receiver object on the UART 1
    def __init__(self, NumChannels: int):
        self.results = [.5]*NumChannels
        self.uart = UART(0, 115200, tx = Pin(0), rx = Pin(1)) # uart1 tx-pin 4, rx-pin 5
        self.numChannels = NumChannels
        

    # Reads the receiver if any new information is available
    def ReadReceiver(self):
        anyu = self.uart.any()
        if anyu>=32:
            self.__handleUART()

    
    # Returns a value from a channel with minimum of that channel set by mn and the maximum set as mx
    def MappedChannel(self, chan: int, mn: float, mx: float) -> float:
        return mapFromNormalized(self.results[chan], mn, mx)

    # Returns a channel as a two position switch
    def TwoPosSwitchChannel(self, chan: int)->bool:
        return self.results[chan]>.5
    # Returns a channel reading as a three position switch
    def ThreePosSwitchChannel(self, chan: int)->int:
        v = self.results[chan]
        if v<.3:
            return 0
        elif v>=.3 and v<.7:
            return 1
        else: 
            return 2 
            
    def __handleUART(self) -> None:
        c=self.uart.read(32)
        if c==None or len(c)!=32:  #There was some problem reading, stick with last, well read values
            return
        if (c[0:2]!=self.__header):  #There was some coruption of the header, stick with last, well read values
            return
        
        index = 0
        for i in range(2,2+2*self.numChannels,2):
            lsb = c[i]
            msb = c[i+1]
            self.results[index] = normal(int(msb)*255+int(lsb),1000,2000)
            index+=1

