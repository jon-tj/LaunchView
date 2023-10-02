from multiprocessing import Process, Queue
from datetime import datetime
from py.serial_reader import serial_reader, send_single_command
from py.csv_data_writer import csv_data_writer


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

    def __init__(self):
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
        self.data={}
        
        data_keys = ['t', 'counter', 'a_x', 'a_y', 'a_z', 'mag_x', 'mag_y', 'mag_z', 'gyro_x', 'gyro_y', 'gyro_z', 'GPS_lat', 'GPS_long', 'alt', 'temp', 'p_mBar', 'GPS_fix', 'recovery_phase', 'recovery_status', 'angle_est', 'rssi', 'snr']
        for k in data_keys: self.data[k] = []

        self.recording=False
        self.p1_read_serial_data = Process(target=serial_reader, args=(self.data_q, self.command_q))
        self.p2_write_to_csv_file = Process(target=csv_data_writer, args=(self.csv_queue,))

    def set_recording_state(self,recording=True):
        if self.p1_read_serial_data.is_alive() == False:    # Might not be necessary to do this here. Not too important though.
            self.p1_read_serial_data.start()
            self.p2_write_to_csv_file.start()
        self.recording = recording
        print(f"Recording {'started' if recording else 'paused'}")

    def get_status(self,request):
        if request in self.status:
            return self.status[request]
        else: return False

    def receive_data(self):
        success = True
        received_data = self.data_q.get()
        #t = received_data[0] / 25  # Should be in the CSV file.

        if self.recording:
            self.csv_queue.put(received_data)

        if received_data[2] != 170:
            print(f"ERROR: PLOT variable error detected. Plots will not be updated {datetime.now()}.")
            self.missed_packages_counter += 1
        else:  # If the data is valid (plot == 170), add it to the data dictionary.
            self.missed_packages_counter = 0

            data_keys = ['t', 'counter', 'a_x', 'a_y', 'a_z', 'mag_x', 'mag_y', 'mag_z', 'gyro_x', 'gyro_y', 'gyro_z', 'GPS_lat', 'GPS_long', 'alt', 'temp', 'p_mBar', 'GPS_fix', 'recovery_phase', 'recovery_status', 'angle_est', 'rssi', 'snr']

            for i, key in enumerate(data_keys):
                self.data[key].append(received_data[i])
            """
            if len(self.data['t']) >= self.ARRAY_SIZE:  # If the data dictionary is too long, remove the oldest data.
                for key in data_keys:
                    self.data[key].pop(0)
            """

        return success
    
    def close(self):
        self.p1_read_serial_data.terminate()
        self.p2_write_to_csv_file.terminate()

    def send_command(self, command):
        if self.p1_read_serial_data.is_alive():
            self.command_q.put((command))
        else:
            send_single_command(command)