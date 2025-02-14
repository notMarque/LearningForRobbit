from pioquadencoderneater import PIOQuadEncoder
import time

quads = PIOQuadEncoder([16, 18, 20], 700,  False)


i = 0
while True:
    try:
        print(i, "\t", quads.getRawData(0))
        time.sleep_ms(1)
        i += 1
    except KeyboardInterrupt:
        quads.stopEncoders()
        print("Ended by Keyboard Interrupt")
        break


