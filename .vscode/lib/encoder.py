#https://cdn.sparkfun.com/datasheets/Robotics/How%20to%20use%20a%20quadrature%20encoder.pdf

import utime

from machine import Pin, Timer
#doFunc is a function called when an encoder is ticked. default to nothing. when used as part of a pid controller can be used to set new values for the motor faster than a main control loop
class Encoder:    
    def __init__(self, pinNumA, pinNumB, watchFunc = lambda p: p):
        self.APin = Pin(pinNumA, Pin.IN)
        self.BPin = Pin(pinNumB, Pin.IN)
        self.APin.irq(self.PinIntA, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        self.BPin.irq(self.PinIntB, Pin.IRQ_FALLING | Pin.IRQ_RISING)
        
        self.lastState = 0b00
        self.currState = 0b00
        
        self.aVal = int(self.APin.value())
        self.bVal = int(self.BPin.value())
        
        self.last0PositionTime = utime.ticks_us()
        self.lastPosition = 0
        self.rpm = 0

        
        self.pos = 0

        invalid = 2
        self.Control = [0, -1, 1, invalid,1,0,invalid,-1,-1,invalid, 0, 1, invalid, 1, -1, 0]
        
        self.tim = Timer()
        self.tim.init(mode=Timer.PERIODIC, period=10, callback=self.CalcRPM)
        
        
        self.watcher = watchFunc
        
    def calcDir(self):
        self.currState = self.aVal*2 + self.bVal
        delta = self.Control[self.lastState*4 + self.currState]
        self.pos+=delta
        self.lastState = self.currState
        
        #self.CalcRPM()        
        self.watcher(self.pos)
        
    def PinIntA(self,p):
        self.aVal = p.value()
        self.calcDir()
    def PinIntB(self,p):
        self.bVal = p.value()
        self.calcDir()
        
    def CalcRPM(self, t):
        #calc dt
        now = utime.ticks_us()
        usecs = utime.ticks_diff(now, self.last0PositionTime)
        dT=(usecs/1000)/1000
        ticks = (self.pos - self.lastPosition)
        rotations = (ticks/540)
        rps = rotations / dT
        self.rpm = rps*60
            
        self.last0PositionTime = now
        self.lastPosition = self.pos
        
    def getPosition(self):
        return self.pos


        
