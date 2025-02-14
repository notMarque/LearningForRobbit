from hmotor import HMotor
from pioquadencoderdma import PIOQuadEncoder

class EncodedMotor(HMotor):
    
    # Constructs encoded motor with same parameters as an HMoto but with encoder pins at end
    def __init__(self, pin1num: int, pin2num: int, pinPWMnum: int, minThreshhold: float, reverse: bool, brakeMode: bool, encoder: PIOQuadEncoder, encoderId: int):
        super().__init__(pin1num, pin2num, pinPWMnum, minThreshhold, reverse, brakeMode)
        self.encoder = encoder
        self.encoderId = encoderId

    # recreates encoder getPos
    def getPos(self):
        return self.encoder.getPos(self.encoderId)
    
    # recreates encoder getVelocity
    def getVelocity(self):
        return self.encoder.getVelocity(self.encoderId)
