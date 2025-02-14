from hmotor import *
import utime

m = HMotor(12, 11, 10, 0.2, False, True)

m.setOutput(0.5)
print("Go")
utime.sleep(2)
print("Stop")
m.setOutput(0.0)