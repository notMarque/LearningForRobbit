from encodedmotor import EncodedMotor 
from pidcontroller import PIDController

# a class to drive a joint to a desired angle
class ServoedJoint:
    # constructs instance using an instance of EncodedMotor, the desired start pos, and p, i, and d values
    def __init__ (self, em: EncodedMotor, startPos: int, p, i, d):
        self.motor = em

        # limits for joint
        self.bounded = False
        self.lowerBound = 0
        self.upperBound = 0

        # encoder offset
        self.offset = startPos

        # PID controller declaration
        self.pid = PIDController(p, i, d)

    # returns joint position(encoder position with offset)
    def getPos(self):
        return self.motor.getPos() + self.offset
    
    # returns velocity of encoder
    def getVelocity(self):
        return self.motor.getVelocity()

    # sets offset to make current motor position zero
    def zero(self):
        self.offset = - self.motor.getPos()
    
    # sets offset to make current position desired position
    def setPos(self, newOffset: int):
        self.zero()
        self.offset += newOffset

    # calls to brake motor
    def brake(self):
        self.motor.brake()

    # calls to coast motor
    def coast(self):
        self.motor.coast()

    # checks bounds and calls PIDController for desired position 
    def driveJoint(self, p: int, modifier):
        pos = p
        limited = False

        # ensure that desired position is within specified range
        if self.bounded == True:
            if pos < self.lowerBound:
                pos = self.lowerBound
                limited = True

            elif pos > self.upperBound:
                pos = self.upperBound
                limited = True

        # drive motor from PID loop with offset for feed forward or other modifications
        val = ( self.pid.updatePID(pos, self.getPos()) + modifier)
        self.motor.setOutput( val)

        # returns false if desired position was unavailable
        return not(limited)
    
    # sets bounds and activates them
    def setBounds(self, min: int, max: int):
        self.bounded = True
        self.lowerBound = min
        self.upperBound = max

    # deactivates the bounds
    def clearBounds(self):
        self.bounded = False
