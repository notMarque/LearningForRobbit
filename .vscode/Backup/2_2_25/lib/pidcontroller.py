
class PIDController:
    
    def __init__ (self, p: float, i: float, d: float):
        self.pVal = p
        self.iVal = 0
        self.dVal = 0
        self.lastPos = 0
        self.integral = 0

    # method to take in desired and current positions and return control value
    # must be called at constant frequency for repeatable results
    def updatePID(self, desired, current):   
        sum = 0

        # calculate proportional value
        sum += self.pVal * (desired-current)
        # calculate integral value
        
        # !!!!!TRY COMENTING OUT FOLLOWING LINE!!!!!
        self.integral += desired-current
        sum += self.iVal * (self.integral + desired - current)
        # calculate derivative value
        sum += self.dVal * (current - self.lastPos)

        return sum



