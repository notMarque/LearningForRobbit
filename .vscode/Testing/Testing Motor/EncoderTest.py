import utime
from quadencoder import *

encoder = QuadEncoder(16, 17)

while True:
    print(str(str(encoder.getPos()) + '       ' + str(encoder.getVelocity())))
    utime.sleep_ms(100)
