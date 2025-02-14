import machine
import time
freq = 270000000
speed = str(round(machine.freq()/1000000,1))
print("The starting speed is",speed,"MHz")
print("Starting the test in 3 seconds")
time.sleep(3)

machine.freq(freq)
speed = str(round(machine.freq()/1000000,1))
print("The current speed is",speed,"MHz")
time.sleep(2)