from servoedjoint import ServoedJoint
from encodedmotor import EncodedMotor
from diffydrive import DiffyDrive

from ibusreciever import IBusReceiver
import utime

rcv = IBusReceiver(14)
lem = EncodedMotor(13, 14, 15, 0.2, False, True, 16, 17)
rem = EncodedMotor(12, 11, 10, 0.2, False, True, 18, 19)

lj = ServoedJoint(lem, 0, 5, 0, 0)
rj = ServoedJoint(rem, 0, 5, 0, 0)

driveTrain = DiffyDrive(1, 1, 0.7, lj, rj)

while True:
    try:
        utime.sleep_ms(5)
        rcv.ReadReceiver()
        driveTrain.drive(rcv.MappedChannel(1, -1, 1), rcv.MappedChannel(3, 1, -1))

        # print(em.getPos(), ";", em.getVelocity())
        print(rcv.MappedChannel(0, 1, -1), "\t", rcv.MappedChannel(1, -1, 1), "\t", rcv.MappedChannel(2, -1, 1), "\t", rcv.MappedChannel(3, 1, -1))
    except KeyboardInterrupt:
        print("Keyboard Interrupt: Motors Stopped")
        driveTrain.brake()
        break