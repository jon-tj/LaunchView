import csv
from datetime import datetime

def csv_data_writer(queue):

    """
    Reads raw data from the main process and writes that data into a csv file for storage.
    """

    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y_%H:%M")

    filename = f"launch_data/launch_data_{dt_string}.csv"

    with open(filename, 'w', newline='') as csvfile:

        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow(['t', 'counter', 'int_var', 'a_x', 'a_y', 'a_z', 'mag_x', 'mag_y', 'may_z', 'gyro_x', 'gyro_y', 'gyro_z', 'GPS_lat', 'GPS_long', 'alt', 'temp', 'p_mBar', 'GPS_fix', 'recovery_phase', 'recovery_status', 'angle_est', 'rssi', 'snr', 'countdown'])

        while True:

            t, counter, plot, a_x, a_y, a_z, mag_x, mag_y, mag_z, gyro_x, gyro_y, gyro_z, GPS_lat, GPS_long, alt, temp, p_mBar, GPS_fix, recovery_phase, recovery_status, angle_est, rssi, snr = queue.get() 

            csvwriter.writerow([t, counter, plot, a_x, a_y, a_z, mag_x, mag_y, mag_z, gyro_x, gyro_y, gyro_z, GPS_lat, GPS_long, alt, temp, p_mBar, GPS_fix, recovery_phase, recovery_status, angle_est, rssi, snr])