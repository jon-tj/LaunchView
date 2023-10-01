from datetime import datetime as date

path_to_csv = f'launch_data/launch_data_{date.today()}.csv'

class DataManager:
    def __init__(self):
        self.data={}
        self.record = False
    
    def get_new_data(self):
        """
        Get updated serial data from serial process and add to the data dictionary.
        """

        #tracemalloc.start()

        counter, plot, a_x, a_y, a_z, mag_x, mag_y, mag_z, gyro_x, gyro_y, gyro_z, GPS_lat, GPS_long, alt, temp, p_mBar, GPS_fix, recovery_phase, recovery_status, angle_est, rssi, snr = self.data_q.get()      # Receive data from serial process. 
        
        t = counter / 25    # Should be in csv file.

        if self.CSV_ACTIVE:
            self.csv_queue.put((t, counter, plot, a_x, a_y, a_z, mag_x, mag_y, mag_z, gyro_x, gyro_y, gyro_z, GPS_lat, GPS_long, alt, temp, p_mBar, GPS_fix, recovery_phase, recovery_status, angle_est, rssi, snr))


        # Do this in the serial process instead (?)
        #if self.PROGRAM == 1 or self.PROGRAM == 2:
        #    self.csv_queue.put((counter, plot, a_x, a_y, a_z, mag_x, mag_y, mag_z, gyro_x, gyro_y, GPS_lat, GPS_long, alt, temp, p_mBar, GPS_fix, recovery_phase, recovery_status, angle_est, rssi))    # Send data to csv process.
        
        if plot == 170:    # If the data is valid, add it to the data dictionary. Status 170 means plots are OK.
            
            self.missed_packages_counter = 0

            self.data['t'].append(t)
            self.data['counter'].append(counter)
            self.data['a_x'].append(a_x)
            self.data['a_y'].append(a_y)
            self.data['a_z'].append(a_z)
            self.data['mag_x'].append(mag_x)
            self.data['mag_y'].append(mag_y)
            self.data['mag_z'].append(mag_z)
            self.data['gyro_x'].append(gyro_x)
            self.data['gyro_y'].append(gyro_y)
            self.data['gyro_z'].append(gyro_z)
            self.data['GPS_lat'].append(GPS_lat)
            self.data['GPS_long'].append(GPS_long)
            self.data['alt'].append(alt)
            self.data['temp'].append(temp)
            self.data['p_mBar'].append(p_mBar)
            self.data['GPS_fix'].append(GPS_fix)
            self.data['recovery_phase'].append(recovery_phase)
            self.data['recovery_status'].append(recovery_status)
            self.data['angle_est'].append(angle_est)
            self.data['rssi'].append(rssi)
            self.data['snr'].append(snr)

            if len(self.data['t']) >= self.ARRAY_SIZE:    # If the data dictionary is too long, remove the oldest data.
                self.data['t'].pop(0)
                self.data['counter'].pop(0)
                self.data['a_x'].pop(0)
                self.data['a_y'].pop(0)
                self.data['a_z'].pop(0)
                self.data['mag_x'].pop(0)
                self.data['mag_y'].pop(0)
                self.data['mag_z'].pop(0)
                self.data['gyro_x'].pop(0)
                self.data['gyro_y'].pop(0)
                self.data['GPS_lat'].pop(0)
                self.data['GPS_long'].pop(0)
                self.data['alt'].pop(0)
                self.data['temp'].pop(0)
                self.data['p_mBar'].pop(0)
                self.data['GPS_fix'].pop(0)
                self.data['recovery_phase'].pop(0)
                self.data['recovery_status'].pop(0)
                self.data['angle_est'].pop(0)
                self.data['rssi'].pop(0)
                self.data['snr'].pop(0)