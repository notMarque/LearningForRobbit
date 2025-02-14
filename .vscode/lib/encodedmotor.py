from hmotor import HMotor
from quadencoder import QuadEncoder

class EncodedMotor(HMotor):
    
    # Constructs encoded motor with same parameters as an HMoto but with encoder pins at end
    def __init__(self, pin1num: int, pin2num: int, pinPWMnum: int, minThreshhold: float, reverse: bool, brakeMode: bool, encoderA: int, encoderB: int):
        super().__init__(pin1num, pin2num, pinPWMnum, minThreshhold, reverse, brakeMode)
        self.encoder = QuadEncoder(encoderA, encoderB)

    # recreates encoder getPos
    def getPos(self):
        return self.encoder.getPos()
    
    # recreates encoder getVelocity
    def getVelocity(self):
        return self.encoder.getVelocity()
