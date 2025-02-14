from pioquadencoder import PIOQuadEncoder
import time

quads = PIOQuadEncoder([16, 18])

while True:
    try:
        print(quads.getTickPos(0), "\t", quads.getTickVelocity(0))
        time.sleep_ms(10)
    except KeyboardInterrupt:
        print("Ended by Keyboard Interrupt")
        break


