import pyquaternion as pq

class OrientationService:
    def __init__(self):
        self.orientationQ = pq.Quaternion(real=1.0, imaginary=(0.0, 0.0, 0.0))
        self.rotation = self.orientationQ.degrees
        self.axis = self.orientationQ.axis
        self.missed_packages_counter = 0                    # NB!
        self.phase = 0                                      # NB!
        self.angle_estimate = 0

    def estimate_orientation(self):
        if self.missed_packages_counter == 0:
            self.angle_estimate = self.data["angle_est"][-1]
        else:
            return None
        return self.angle_estimate
    
    def euler_angles(self):
        return self.estimate_orientation().to_euler_angles()