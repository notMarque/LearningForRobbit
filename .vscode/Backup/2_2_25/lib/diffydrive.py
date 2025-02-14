class DiffyDrive:
    def __init__(self, scaleDrive, scaleTurn, maxSpeed, lMotor: ServoedJoint, rMotor: ServoedJoint):
        self.scaleDrive = scaleDrive
        self.scaleTurn = scaleTurn
        self.maxSpeed = maxSpeed
        self.lMotor = lMotor
        self.rMotor = rMotor

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
        self.lMotor.driveJointVel(lSpeed * self.maxSpeed, 0)
        self.rMotor.driveJointVel(rSpeed * self.maxSpeed, 0)
    
    # Method to stop drivetrain
    def brake(self):
        self.lMotor.brake()
        self.rMotor.brake()