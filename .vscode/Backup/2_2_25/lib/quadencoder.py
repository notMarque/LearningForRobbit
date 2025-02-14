from machine import Pin, Timer
import machine

# a class to decode quadrature encoders
class QuadEncoder:

    # encoder object constructor
    def __init__ (self, pinAnum: int, pinBnum: int):
        # declare pins and set as interrupts
        self.pinA = Pin(pinAnum, Pin.IN)
        self.pinB = Pin(pinBnum, Pin.IN)

        self.pinA.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.encoderACallback, hard=True)
        self.pinB.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = self.encoderBCallback, hard=True)

        # position variables for velocity calculations
        self.pos = 0
        self.lastPos = 0
        self.lasterPos = 0
        self.TICKS_PER_REV = 700
        self.VELOCITY_CALC_PERIOD = 100
        self.GEARRATIO = 1

        self.avgedVel = 0

        # create timer for velocity calculations
        self.velocityTimer = Timer(mode=Timer.PERIODIC, period=self.VELOCITY_CALC_PERIOD, callback=self.velocityTracker)

        # variables for calculating encoder state
        self.lastState =  0b00 
        self.currState = 0b00

        self.AVal = int(self.pinA.value())
        self.BVal = int(self.pinB.value())

        # logic table for calculating position
        invalid = 2
        self.Control = [0, -1, 1, invalid,1,0,invalid,-1,-1,invalid, 0, 1, invalid, 1, -1, 0]
        
    # method called by timer to automatically track velocity
    def velocityTracker(self, tim):
        self.lasterPos = self.lastPos
        self.lastPos = self.pos

    # interrupt handler for pin A
    def encoderACallback(self, pin):
        # disable interrupt requests to prevent bouncing causing problems
        state = machine.disable_irq()
        
        self.AVal = pin.value()
        self.tick()

        # re-enable interrupt requests
        machine.enable_irq(state)

    # interrupt handler for pin B
    def encoderBCallback(self, pin):
        # disables interrupt rerquest to prevent re-entering
        state = machine.disable_irq()
        
        self.BVal = pin.value()
        self.tick()
        
        # re-enable interrupt requests
        machine.enable_irq(state)

    # method called by handlers to determine position increment
    def tick(self):
        self.currState = self.AVal * 2 + self.BVal
        delta = self.Control[self.lastState*4 + self.currState]
        self.pos += delta
        self.lastState = self.currState
    
    # returns current position in ticks
    def getTickPos(self):
        return int(self.pos / float(self.TICKS_PER_REV) * 360)
    
    # returns average velocity over last VELOCITY_CALC_PERIOD(milliseconds) in ticks per second
    def getTickVelocity(self):
        return (600*(self.lastPos - self.lasterPos))/float(self.TICKS_PER_REV)

    # returns current position in revs
    def getPos(self):
        return float(self.getTickPos()) / float(self.TICKS_PER_REV) / float(self.GEARRATIO)
    
    # returns average velocity over last VELOCITY_CALC_PERIOD(milliseconds) in revs per second
    def getVelocity(self):
        return float(self.getTickVelocity()) / float(self.TICKS_PER_REV) / float(self.GEARRATIO)    
