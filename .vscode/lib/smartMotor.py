from Hardware.encoder import Encoder
from Hardware.PID import PID
from Hardware.motor import Motor

def clamp(v, l, h):

    if v<l:
        return l
    elif v>h:
        return h
    return v
def sign(v):
    if v>=0:
        return 1
    else:
        return -1


class SmartMotor:
    #Encoder, PID Values, Motor, watcher func. called when the encoder ticks. can be watched for odometry or speed information
    def __init__(self, e: Encoder, p: PID, m: Motor, watcherFunc = lambda p: p):
        self.enc = e
        #self.enc.watcher = self.HandleEncoderTick
        self.pid = p
        self.motor = m
        self.watcher = watcherFunc
        self.lastV=0
        self.SetPosition(0)
        
    
    def GetPosition(self):
        return self.enc.pos
    def GetDegrees(self):
        return (self.enc.pos/540.0)*360

    #RPM of encoder
    def GetSpeed(self):
        return self.enc.rpm

    def SetPosition(self, pos):
        self.pid.Set(pos)
        self.pid.lastErr=5
    def SetDegrees(self, deg):
        self.pid.Set((deg/360) * 540)
        self.pid.lastErr=5
        
    def SetPercentOutput(self, x: float):
        self.motor.SetPercentOutput(x)
        
    def GetTarget(self):
        return self.pid.setpoint
    def Stop(self):
        self.motor.brake()
    #used to update pid at a constant frequency
    def Handle(self):
        position = self.enc.pos
    
        motorVal = self.pid.GetControl(position)
        s=sign(motorVal)
        motorVal = s*clamp(abs(motorVal),0.0,1.0)

        self.motor.SetPercentOutput(motorVal)
        self.lastV = motorVal
        self.watcher(position)

