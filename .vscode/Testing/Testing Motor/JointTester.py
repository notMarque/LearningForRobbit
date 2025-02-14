from servoedjoint import ServoedJoint
from encodedmotor2 import EncodedMotor
import machine, math
from pioquadencoder import PIOQuadEncoder


quadEncoders = PIOQuadEncoder([16, 18])
lem = EncodedMotor(13, 14, 15, 0.2, False, True, quadEncoders, 0)
# em = EncodedMotor(13, 14, 15, 0.2, True, True, 16)
# upperMotor = EncodedMotor(18, 17, 16, 0.1, True, True, 9, 10)

j = ServoedJoint(lem, 0, 5, 0, 0)
# j2 = ServoedJoint(upperMotor, 0, 0.07, 0, 0)
# pot1 = machine.ADC(28)
# pot2  = machine.ADC(27)


i = 0

while i < 3000:
    # j.driveJoint(1*(int((65535-pot1.read_u16())  * 180 / 65535))-90, 0*math.sin(math.radians(j.getPos())))
    # j2.driveJoint(1*(int(pot2.read_u16()  * 180 / 65535))-90, 0)
    # j.driveJointVel(.52, 0)
    #lem.setOutput(.5)
    j.driveJointVel(0.5, 0)
    # math.sin(math.radians(j.getPos()))
    print(str(lem.getVelocity())) # + ' ' + str(em.getPower()))#  + '        ' + str(upperMotor.getPos()) + ' ' + str(upperMotor.getPower()))
    i += 1

j.brake()