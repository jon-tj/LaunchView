import csv
from datetime import datetime

path_to_csv = f'launch_data/launch_data_{datetime.today()}.csv'

def csv_data_writer(queue): # <-- expects data stream queue
    """
    Reads from the data queue process and writes to path_to_csv.
    """
    with open(path_to_csv, 'w', newline='') as f:
        wr = csv.writer(f)
        #wr.writerow(['t', 'counter', 'int_var', 'a_x', 'a_y', 'a_z', 'mag_x', 'mag_y', 'may_z', 'gyro_x', 'gyro_y', 'gyro_z', 'GPS_lat', 'GPS_long', 'alt', 'temp', 'p_mBar', 'GPS_fix', 'recovery_phase', 'recovery_status', 'angle_est', 'rssi', 'snr', 'countdown'])
        while True:
            row = queue.get() 
            wr.writerow([entry for entry in row])