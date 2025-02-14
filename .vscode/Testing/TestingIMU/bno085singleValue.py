# BNO085 Micropython I2C Test with single value
# 
# Mark Sommers

from machine import I2C, Pin
import time
import math
from bno08x_i2c import *

I2C1_SDA = Pin(26)
I2C1_SCL = Pin(27)

i2c1 = I2C(1, scl=I2C1_SCL, sda=I2C1_SDA, freq=100000, timeout=200000)
print("I2C Device found at address: ", i2c1.scan(), "\n")

bno = BNO08X_I2C(i2c1, debug=False)
print("BNO085 I2C connection: Done\n")

# bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
# bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

print("BNO085 sensors enabling: Done\n")

timeLast = time.ticks_ms()

while True:
    try:
        gyro_x, gyro_y, gyro_z = bno.gyro
        timeNow = time.ticks_ms()
        timeDif = timeNow - timeLast
        timeLast = timeNow
        # print("\tTime(ms): ", timeDif)
        print("Gyroscope\tX: %0.6f\tY: %0.6f\tZ: %0.6f\trad/s" % (gyro_x, gyro_y, gyro_z), "\tTime(ms): ", timeDif)
    except KeyboardInterrupt:
        print("Stopped by KeyboardInterrupt")
        print("\tTime(ms): ", timeDif)
        break