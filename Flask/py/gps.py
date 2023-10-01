class GPS:
    def __init__(self):
        self.alive = False
        self.latitude=0
        self.longitude=0
    def get_coordinates(self):
        self.latitude=-1
        self.longitude=-1
        return self.latitude, self.longitude