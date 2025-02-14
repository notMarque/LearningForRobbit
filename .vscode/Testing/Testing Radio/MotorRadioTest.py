from servoedjoint import ServoedJoint
from encodedmotor import EncodedMotor

from ibusreciever import IBusReceiver
import utime

rcv = IBusReceiver(14)
em = EncodedMotor(13, 14, 15, 0.2, True, True, 16, 17)

j = ServoedJoint(em, 0, 5, 0, 0)

while True:
    try:
        rcv.ReadReceiver()
        utime.sleep_ms(5)
        j.driveJointVel(rcv.MappedChannel(4, -.7, .7), 0)

        print(em.getPos(), ";", em.getVelocity())
        # print(rcv.MappedChannel(0, 1, -1), "\t", rcv.MappedChannel(1, -1, 1), "\t", rcv.MappedChannel(2, -1, 1), "\t", rcv.MappedChannel(3, 1, -1))
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        j.brake()
        break