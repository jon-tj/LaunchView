from multiprocessing import Process, Queue
class TelemetryService:
    """
    # Received telemetry messages 
    bit   | function                          | notes
    ------|-----------------------------------|--------------------
    15    | pre_launch_referanse satt         | settes når 'launch soon' er mottatt+kalibrering utført
    14    | magnetometer reference OK         |
    13    | accelerometer comms OK            |
    12    | magnetometer comms OK             |
    11    | gyroscope comms OK                |
    10    | dangerous angle                   | spoopy angle detected(before separation)
    09    | separation activated              |
    08    | main chute activated              |
    07    | movement direction (up/down)      | 1 = up, 0 = down
    06    | writing live data to flash        |
    05    | protecting flash memory           |
    04    | flash reset performed             |
    03    | telemetri message received        |
    02    | two way comms OK                  |
    01    | telemetry comms OK                |
    00    | sensor system comms OK            |
    """

    def __init__(self,serial_reader,csv_writer):
        self.alive = False
        self.status={
            "pre-launch-ref": False,
            "magnetometer-ref": False,
            "accelerometer": False,
            "magnetometer": False,
            "gyroscope": False,
            "angle-ok": True,
            "separated": False,
            "chute-deployed": False,
            "ascending": False,
            "flash-write": False, # when do we use this??
            "flash-protected": False, # when do we use this??
            "flash-reset": False, # when do we use this??
            "telemetry-msg-received": False,
            "two-way-comms": False,
            "telemetry": False,
            "sensors-ok": True,
        }
        self.data_q= Queue()
        self.command_q = Queue()
        self.csv_queue = Queue()
        self.countdown_q = Queue()
        self.p1_read_serial_data = Process(target=serial_reader, args=(self.data_q, self.command_q))
        self.p2_write_to_csv_file = Process(target=csv_writer, args=(self.csv_queue,))

    def get_status(self,request):
        if request in self.status:
            return self.status[request]
        else: return False

    def receive_data(self):
        success = True
        return success
    
    def try_connect(self):

        self.alive = self.receive_data() # returns True if connection is established
        return self.alive

    def send_command(self, command):
        """
        We assume self.alive==True.
        See commands.py for more information.
        """
