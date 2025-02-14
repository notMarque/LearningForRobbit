def scale(val, min, max):
    return val*(max-min) + min

class DiffyDrive:
    def __innit__(self, scaleDrive, scaleTurn, max, left: ServoedJoint, right: ServoedJoint):
        self.scaleDrive = scaleDrive
        self.scaleTurn = scaleTurn
        self.max = max
        self.lMotor = left
        self.rMotor = right

    def drive(self, drive, turn):
        lSpeed = drive + turn
        rSpeed = drive - turn

        # If left or right value over 1, scale back to within 1 (Prevents weird things that truncating would do)
        if lSpeed > 1:
            lSpeed = lSpeed / lSpeed
            rSpeed = rSpeed / lSpeed
        if rSpeed > 1:
            lSpeed = lSpeed / rSpeed
            rSpeed = rSpeed / rSpeed

        # Drive motors scaled to a max velocity
        self.lMotor.driveJointVel(scale(lSpeed, -self.max, self.max))
        self.rMotor.driveJointVel(scale(rSpeed, -self.max, self.max))
    
    # Method to stop drivetrain
    def brake(self):
        self.lMotor.brake()
        self.rMotor.brake()