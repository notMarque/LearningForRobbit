from machine import Pin, PWM

def clamp(l, h, v):
    if v > h:
        return h
    if v < l:
        return l
    return v

# A generic H-Bridge Library(that was designed for the TB6612 Motor controller)
# https://learn.adafruit.com/adafruit-tb6612-h-bridge-dc-stepper-motor-driver-breakout/overview

class HMotor:

    # pin1num(GPIO pin), pin2num(GPIO pin), pinPWMnum(PWM pin), minThreshhold(value at which motor switches to brake mode), reverse(reversed if true), brakeMode(true if brake engaged instead of coast)
    def __init__(self, pin1num: int, pin2num: int, pinPWMnum: int, minThreshhold: float, reverse: bool, brakeMode: bool):
        self.Pin1 = Pin(pin1num, Pin.OUT)
        self.Pin2 = Pin(pin2num, Pin.OUT)

        self.pwm = PWM(Pin(pinPWMnum))
        self.pwm.freq(100000)

        self.power = 0
        self.reverse = reverse
        self.brakeMode = brakeMode
        self.minThreshhold = minThreshhold
        self.brakeThreshhold = 0.01

    def setOutput(self, p: float):
        # Ensure motor value is in acceptable range
        self.power = clamp(-1, 1, p)

        # Check if motor is reversed and negate power value
        if self.reverse:
            self.power *= -1

        # Checks if motor should be stopped due to threshold
        if abs(self.power) <= self.minThreshhold:
            if self.brakeMode:
                self.brake()
            else:
                self.coast()

        # sets digital pins for forward rotation and sets PWM duty cycle
        elif self.power > 0:
            self.Pin1.value(0)
            self.Pin2.value(1)
            self.pwm.duty_u16(int(65535*abs(self.power)))

        # sets digital pins for reverse rotation and sets PWM duty cycle
        elif self.power < 0:
            self.Pin1.value(1)
            self.Pin2.value(0)
            self.pwm.duty_u16(int(65535*abs(self.power)))

    def getPower(self):
        return self.power

    def brake(self):
        self.pwm.duty_u16(0)
        self.Pin1.value(1)
        self.Pin2.value(1)

    def coast(self):
        self.pwm.duty_u16(0)
        self.Pin1.value(0)
        self.Pin2.value(0)

