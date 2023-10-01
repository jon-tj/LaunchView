import serial
from serial import *
import random as r
import math as m
import sys
import time as t
import numpy as np
import os
import pyquaternion as pq
import webbrowser
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, 
    QVBoxLayout, QGridLayout, QGroupBox, QTabWidget, QToolBar, QLabel, QLineEdit, QSlider
)
from pyqtgraph import PlotWidget
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem
from stl import mesh
from multiprocessing import Process, Queue

from functions import *
from csv_data_writer import csv_data_writer
from serial_reader import serial_reader, send_single_command
#from countdown import countdown


########## Declare global variables. ##########

"""
Program 1: Live data received through telemetry, write data to a csv file.
Program 2: Fake data generated in a process, writes data to a csv file.
Program 3: Visualize existing data from a csv file.

"""

class MainWindow(QMainWindow):

    REFRESH_RATE = 10                                                           # Defines how many iterations of the main loop will pass between updating plots. Greater numbers makes faster plots.
    PLOT_COUNTER = 0                                                            # Counter used to keep track of how many iterations of the program has passed.        
    ARRAY_SIZE = 100                                                            # How large the lists will be before values are popped before adding new values. Remove this. 
    FIRST_TIME_MEASUREMENT = None
    START_CLICKED = False
    CSV_ACTIVE = False                                                          # Remove. This button caused the failure of CSV process.


    # Plot colours:

    BACKGROUND = (66, 73, 82)  # RGB
    MBLUE = (0, 0.4479*255, 0.7410*255)
    MORANGE = (0.85*255, 0.3250*255, 0.0980*255)
    MSOMECOLOR = (0.69*255, 0.3250*255, 0.06969*255)

    # Not currently in use:

    PROGRAM = 1
    SIMULATION_FILENAME = 'launch_data/launch_data_28.03.2023_18:26.csv'        # Filename of the simulation data.
    T_MINUS = -75 * 60                                                          # 75 minutes (in seconds) to launch.
    LAST_TEN_GPS = []
    GPS_MAP_ON = False
    FIRST_TAB_OPENED = False
    gps_lat = " "
    gps_long = " "

    GROUND = 0
    IMMINENT = 1
    ACCELERATION = 2
    FALLING = 3
    DROGUE = 4
    MAIN = 5
    LANDED = 6

    PHASES = {
    0: 'Phase  1  Rocket on launch pad',
    1: 'Phase  2  Waiting for launch',
    2: 'Phase  3  Burn phase',
    3: 'Phase  4  Burnout',
    4: 'Phase  5  Drogue chute deployed',
    5: 'Phase  6  Main chute deployed',
    6: 'Phase  7  Rocket has landed'
    }

    def __init__(self):
        super().__init__()

        self.data = {
            't': [],
            'counter': [],
            'int_var': [],
            'a_x': [],
            'a_y': [],
            'a_z': [],
            'mag_x': [],
            'mag_y': [],
            'mag_z': [],
            'gyro_x': [],
            'gyro_y': [],
            'gyro_z': [],
            'GPS_lat': [],
            'GPS_long': [],
            'alt': [],
            'temp': [],
            'p_mBar': [],
            'GPS_fix': [],
            'recovery_phase': [],
            'recovery_status': [],
            'angle_est': [],
            'rssi': [],
            'snr': [],

            'countdown': [],
        }
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.showFullScreen()
        self.main_layout = QGridLayout()
        self.main_layout.setColumnStretch(0, 10)
        self.main_layout.setColumnStretch(1, 15)
        self.main_layout.setColumnStretch(2, 7)

        self.main_layout.setRowStretch(0, 10)
        self.main_layout.setRowStretch(1, 10)
        self.main_layout.setRowStretch(2, 10)
        self.main_layout.setRowStretch(3, 10)
        self.main_layout.setRowStretch(4, 5)

        self.main_widget.setLayout(self.main_layout)
        self.set_up_timer()
        self.set_up_plots()
        self.set_up_3D_display()
        self.set_up_labels_and_data_layout()
        self.set_up_toolbar()

        # Bjørn
        self.set_up_calculations()
        self.setup_status_labels()

        self.data_q = Queue()
        self.command_q = Queue()
        self.csv_queue = Queue()
        self.countdown_q = Queue()
        self.select_program()

    
    #####################################################################################
    # BJØRN START

    def set_up_calculations(self):
        self.orientationQ = pq.Quaternion(real=1.0, imaginary=(0.0, 0.0, 0.0))
        self.rotation = self.orientationQ.degrees
        self.axis = self.orientationQ.axis
        self.missed_packages_counter = 0                    # NB!
        self.phase = 0                                      # NB!
        self.angle_estimate = 0

    def setup_status_labels(self):
        self.status_labels = [
            QLabel(f'Pre launch offsets:         Not set'),
            QLabel(f'Magnetometer reference      Not set'),
            QLabel(f'Accelerometer:              Offline'),
            QLabel(f'Magnetometer:               Offline'),
            QLabel(f'Gyroscope:                  Offline'),
            QLabel(f'Dangerous angle detected:   No'),
            QLabel(f'Drogue Chute activated:     No'),
            QLabel(f'Main Chute activated:       No'),
            QLabel(f'Positive Vertical Speed:    No'),
            QLabel(f'Writing to flash:           No'),
            QLabel(f'Flash blocked:              No'),
            QLabel(f'Flash Reset performed:      No'),
            QLabel(f'Telemetry ping              No Reply'),
            QLabel(f'Telemetry duplex confirmed: No'),
            QLabel(f'Telemetry handshake         No Reply'),
            QLabel(f'Sensor system handshake     No Reply'),
        ]
        for i, label in enumerate(self.status_labels):
            self.data_layout.addWidget(label, i + 8, 0)
        def setStatus(i,msg,status="success"):
            self.status_labels[i].setText(msg+":"+" "*(28-len(msg))+status)
        self.status_actions = {      # actions to take depending on status bytes
            0: lambda bit: setStatus(0,'Pre launch offsets',"Set" if int(bit) else "Not set"),   # reference values set by launch imminent message
            1: lambda bit: self.status_labels[1].setText(f'Magnetometer reference      Set') if int(bit) else self.status_labels[1].setText(f'Magnetometer reference      Not set'),   # magnetometer reference set
            2: lambda bit: self.status_labels[2].setText(f'Accelerometer:              Online') if int(bit) else self.status_labels[2].setText(f'Accelerometer:              Offline'),   # accel comms OK
            3: lambda bit: self.status_labels[3].setText(f'Magnetometer:               Online') if int(bit) else self.status_labels[3].setText(f'Magnetometer:               Offline'),   # magnet comms OK
            4: lambda bit: self.status_labels[4].setText(f'Gyroscope:                  Online') if int(bit) else self.status_labels[4].setText(f'Gyroscope:                  Offline'),   # gyro comms OK
            5: lambda bit: self.status_labels[5].setText(f'Dangerous angle detected:   Yes') if int(bit) else self.status_labels[5].setText(f'Dangerous angle detected:   No'),   # dangerous angle detected
            6: lambda bit: self.status_labels[6].setText(f'Drogue Chute activated:     Yes') if int(bit) else self.status_labels[6].setText(f'Drogue Chute activated:     No'),   # drogue chute deployed
            7: lambda bit: self.status_labels[7].setText(f'Main Chute activated:       Yes') if int(bit) else self.status_labels[7].setText(f'Main Chute activated:       No'),   # main chute deployed
            8: lambda bit: self.status_labels[8].setText(f'Positive Vertical Speed:    Yes') if int(bit) else self.status_labels[8].setText(f'Positive Vertical Speed:    No'),   # movement direction (1=up, 0=down)
            9: lambda bit: self.status_labels[9].setText(f'Writing to flash:           Yes') if int(bit) else self.status_labels[9].setText(f'Writing to flash:           No'),   # writing to flash
            10: lambda bit: self.status_labels[10].setText(f'Flash blocked:              Yes') if int(bit) else self.status_labels[10].setText(f'Flash blocked:              No'),  # flash memory blocked from writing
            11: lambda bit: self.status_labels[11].setText(f'Flash Reset performed:      Yes') if int(bit) else self.status_labels[11].setText(f'Flash Reset performed:      No'),  # flash reset performed
            12: lambda bit: self.status_labels[12].setText(f'Telemetry ping              Message received') if int(bit) else self.status_labels[12].setText(f'Telemetry ping              No Reply'),  # recent message from telemetry
            13: lambda bit: self.status_labels[13].setText(f'Telemetry duplex confirmed: Yes') if int(bit) else self.status_labels[13].setText(f'Telemetry duplex confirmed: No'),  # duplex communication confirmed
            14: lambda bit: self.status_labels[14].setText(f'Telemetry handshake         OK') if int(bit) else self.status_labels[14].setText(f'Telemetry handshake         No Reply'),  # telemetry handshake OK
            15: lambda bit: self.status_labels[15].setText(f'Sensor system handshake     OK') if int(bit) else self.status_labels[15].setText(f'Sensor system handshake     No Reply'),  # sensors handshake OK
        }

    def data_in_lists(self):
        return len(self.data['t']) > 0

    def decode_and_calculations(self):

        # decode status byte
        # bit #     || function                          || notes
	    # ----------||-----------------------------------||--------------------
	    # bit 15    || pre_launch_referanse satt         || settes når launch soon-beskjed er mottatt og referanser/kalibrering er utført
	    # bit 14    || magnetometer reference OK         ||
	    # bit 13    || accelerometer comms OK            ||
	    # bit 12    || magnetometer comms OK             ||
	    # bit 11    || gyroscope comms OK                ||
	    # bit 10    || dangerous angle                   || no separation yet, but dangerous angle detected
	    # bit 09    || separation activated              ||
	    # bit 08    || main chute activated              ||
	    # bit 07    || movement direction (up/down)      || 1 = up, 0 = down
	    # bit 06    || writing live data to flash        ||
	    # bit 05    || protecting flash memory           ||
	    # bit 04    || flash reset performed             ||
	    # bit 03    || telemetri message received        ||
	    # bit 02    || two way comms OK                  ||
	    # bit 01    || telemetry comms OK                ||
	    # bit 00    || sensor system comms OK            ||

        if self.data_in_lists():

            status_u16 = '{0:b}'.format(self.data['recovery_status'][-1])
            status_u16 = '0'*(16-len(status_u16)) + status_u16                # format into bit-string of length 16

            for i, bit in enumerate(status_u16):
                self.status_actions[i](bit)

            # decode phase

            self.phase_label.setText(self.PHASES[self.data['recovery_phase'][-1]])

            # calculate angle

            # calculate angle
            if self.missed_packages_counter == 0:
                self.rocket_mesh.rotate(-self.angle_estimate, 0, 1, 0)
                self.angle_estimate = self.data["angle_est"][-1]
                self.rocket_mesh.rotate(self.angle_estimate, 0, 1, 0)

                self.angle_estimate_label.setText(f"Angle estimate: {int(self.angle_estimate)}°")


            """ acc_bodyQ = pq.Quaternion(w=0.0, x=self.data['a_x'][-1], y=self.data['a_y'][-1], z=self.data['a_z'][-1])           # vektorkvaternion for akselerasjon
            mag_bodyQ = pq.Quaternion(w=0.0, x=self.data['mag_x'][-1], y=self.data['mag_y'][-1], z=self.data['mag_z'][-1])     # vektorkvaternion for akselerasjon

            gyroX, gyroY, gyroZ = self.data['gyro_x'][-1], self.data['gyro_y'][-1], self.data['gyro_z'][-1]                    # gyromålinger
            gyro_length = m.sqrt(gyroX**2 + gyroY**2 + gyroZ**2)                                                               # lengde av gyrovektor (= total rotert vinkel)
            rot_angle = gyro_length*(1+self.missed_packages_counter) * 40                                                      # timestep = 40 ms * missed packages

            gyro_rotQ = pq.Quaternion(degrees=rot_angle, axis=(gyroX, gyroY, gyroZ))    # finn rotasjon siste tidsskritt
            gyro_orientation = self.orientationQ * gyro_rotQ

            # rotate acceleration quaternion to find down direction world coordinates
            acc_worldQ = (gyro_orientation * acc_bodyQ * gyro_orientation.inverse).normalised
            acc_vec = np.array([acc_worldQ.x, acc_worldQ.y, acc_worldQ.z])
            acc_length = m.sqrt(acc_vec[0]**2 + acc_vec[1]**2 + acc_vec[2]**2)
            up = np.array([0, 0, 1])

            # find rotation describing difference between accelerometer and gyro orientation
            dot_prod_norm = np.dot(acc_vec, up)/acc_length
            # avoid invalid argument to acos
            if dot_prod_norm > 1.0:
                dot_prod_norm = 1.0
            elif dot_prod_norm < -1.0:
                dot_prod_norm = -1.0
            acc_corrAngle = (180*np.arccos(dot_prod_norm))/np.pi  # angle in degrees
            acc_corrAxis = np.cross(acc_vec, up)   # axis

            # find appropriate weight for accelerometer correction
            if self.phase == self.GROUND or self.phase == self.LANDED:
                rho = 18.0
                lambd = 2.0
            else:
                rho = 64.0
                lambd = 16.0
            acc_diffLength = 1 - m.sqrt(self.data['a_x'][-1]**2 + self.data['a_y'][-1]**2 + self.data['a_z'][-1]**2)
            alpha = 1 / (1 + rho*acc_diffLength**2)
            weight = alpha / (alpha + lambd)

            if not (self.phase == self.GROUND or self.phase == self.LANDED):  # dupliserer bare C-koden her. eksperimenterer med hvordan å tweake estimeringen
                weight = 0.0

            # construct quaternion describing the rotation for the difference, weighted with variable <weight>
            acc_corrQ = pq.Quaternion(degrees=weight*acc_corrAngle, axis=(acc_corrAxis))

            # Rotate gyro estimate "a little" (designated by weight)
            self.orientationQ = acc_corrQ * gyro_rotQ """

        else:

            pass

    # BJØRN STOPP
    #####################################################################################


    def set_up_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(20) # milliseconds
        self.timer.timeout.connect(self.update_gui)
        
        self.countdown_timer = QtCore.QTimer()
        self.countdown_timer.setInterval(1000) # milliseconds
        self.countdown_timer.timeout.connect(self.update_countdown)

    
    def set_up_plots(self):
        self.plot_altitude = PlotWidget()
        self.plot_altitude.addLegend()
        self.plot_altitude.showGrid(x=True, y=True)
        self.plot_altitude.setTitle('Altitude')
        self.plot_altitude.setBackground(self.BACKGROUND)
        self.plot_altitude.setLabel('left', 'meters')
        self.plot_altitude.setLabel('bottom', 'time', units='s')
        self.plotline_alt = self.plot_altitude.plot(self.data['t'], self.data['alt'], name='altitude(t)', pen=self.MBLUE)
        self.main_layout.addWidget(self.plot_altitude, 0, 0)

        self.plot_acceleration = PlotWidget()
        self.plot_acceleration.addLegend()
        self.plot_acceleration.showGrid(x=True, y=True)
        self.plot_acceleration.setTitle('Acceleration')
        self.plot_acceleration.setBackground(self.BACKGROUND)
        self.plot_acceleration.setLabel('left', 'm/s^2')
        self.plot_acceleration.setLabel('bottom', 'time', units='s')
        self.plotline_a_x = self.plot_acceleration.plot(self.data['t'], self.data['a_x'], name='x-axis', pen=self.MBLUE)
        self.plotline_a_y = self.plot_acceleration.plot(self.data['t'], self.data['a_y'], name='y-axis', pen=self.MORANGE)
        self.plotline_a_z = self.plot_acceleration.plot(self.data['t'], self.data['a_z'], name='z-axis', pen=self.MSOMECOLOR)
        self.main_layout.addWidget(self.plot_acceleration, 1, 0)

        self.plot_rssi = PlotWidget()
        self.plot_rssi.addLegend()
        self.plot_rssi.showGrid(x=True, y=True)
        self.plot_rssi.setTitle('RSSI')
        self.plot_rssi.setBackground(self.BACKGROUND)
        self.plot_rssi.setLabel('left', 'dBm')
        self.plot_rssi.setYRange(-120, 10)
        self.plot_rssi.setLabel('bottom', 'time', units='s')
        self.plotline_rssi = self.plot_rssi.plot(self.data['t'], self.data['rssi'], name='RSSI', pen=self.MBLUE)
        self.main_layout.addWidget(self.plot_rssi, 2, 0)

        self.plot_temperature = PlotWidget()
        self.plot_temperature.addLegend()
        self.plot_temperature.showGrid(x=True, y=True)
        self.plot_temperature.setTitle('Temperature')
        self.plot_temperature.setBackground(self.BACKGROUND)
        self.plot_temperature.setLabel('left', '°C')
        self.plot_temperature.setYRange(-20, 80)
        self.plot_temperature.setLabel('bottom', 'time', units='s')
        self.plotline_T_o = self.plot_temperature.plot(self.data['t'], self.data['temp'], name='Outside temperature', pen=self.MBLUE)
        self.main_layout.addWidget(self.plot_temperature, 3, 0)

        
    def set_up_3D_display(self):
        self.threeD_widg = GLViewWidget()
        self.threeD_widg.setBackgroundColor(self.BACKGROUND)
        stl_mesh = mesh.Mesh.from_file('static/stl/rocket.STL')
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        mesh_data = MeshData(vertexes=points, faces=faces)
        self.rocket_mesh = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=False, drawEdges=True)
        self.threeD_widg.addItem(self.rocket_mesh)
        self.rocket_mesh.rotate(angle=90, x=90, y=0, z=1)
        self.main_layout.addWidget(self.threeD_widg, 0, 1, 4, 1)
        
        self.angle_estimate_label = QLabel(self)
        self.angle_estimate_label.setText("Angle estimate: ")

        self.main_layout.addWidget(self.angle_estimate_label, 0, 1)

        #self.threeD_widg.show()

    
    def set_up_toolbar(self):
        self.toolbar_layout = QHBoxLayout()

        # Create input field and button for user commands.
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Enter command to send to rocket.")
        self.toolbar_layout.addWidget(self.input)
        self.input.returnPressed.connect(self.process_user_command)

        ## Add logo to toolbar.
        #self.logo = QLabel()
        #self.logo.setPixmap(QPixmap('static/images/logo.png').scaled(200, 200))
        #self.toolbar_layout.addWidget(self.logo)

        self.countdown_label = QLabel(self)
        self.countdown_label.setText("t- 01:15:00")
        self.countdown_label.setProperty("class", "countdown_label")
        self.toolbar_layout.addWidget(self.countdown_label)

        self.start_countdown_button = QPushButton("Start")
        self.start_countdown_button.clicked.connect(self.start_countdown)
        self.toolbar_layout.addWidget(self.start_countdown_button)

        self.pause_countdown_button = QPushButton("HOLD")
        self.pause_countdown_button.clicked.connect(self.pause_countdown)
        self.toolbar_layout.addWidget(self.pause_countdown_button)

        self.new_time = QLineEdit(self)
        self.new_time.setPlaceholderText("HH:MM:SS")
        self.new_time.returnPressed.connect(self.edit_countdown)
        self.toolbar_layout.addWidget(self.new_time)

        plot_speed_slider = QSlider()
        plot_speed_slider.setRange(1, 100)
        plot_speed_slider.setValue(10)
        plot_speed_slider.setSingleStep(1)
        plot_speed_slider.valueChanged.connect(self.change_plot_speed)
        self.toolbar_layout.addWidget(plot_speed_slider)

        self.csv_process_toggle_button = QPushButton("CSV NOT ON")
        self.csv_process_toggle_button.setCheckable(True)
        self.csv_process_toggle_button.clicked.connect(self.toggle_csv_process)
        self.toolbar_layout.addWidget(self.csv_process_toggle_button)


        self.main_layout.addLayout(self.toolbar_layout, 4, 0, 1, 3)


    def toggle_csv_process(self, on):
        if on:
            self.CSV_ACTIVE = True
            self.csv_process_toggle_button.setText("CSV IS NOW ACTIVE")
        else:
            self.CSV_ACTIVE = False
            self.csv_process_toggle_button.setText("CSV IS NOT ON    ")


    def change_plot_speed(self, value):
        """
        Change the speed at which the plots are updated based on slider value.
        """
        self.PLOT_COUNTER = 0
        self.REFRESH_RATE = value
        print(f"LAUNCH PROGRAM MESSAGE: Plot speed changed to {value}.")


    def start_countdown(self):
        self.countdown_timer.start()

        ## Initialize geolocator
        #geolocator = Nominatim(user_agent="my_app")

        ## Define the coordinates
        #coordinates = "58°29.4707' N, 6°12.8232' E"

        ## Use geolocator to obtain latitude and longitude values
        #location = geolocator.geocode(coordinates)

        ## Build the URL with the latitude and longitude values
        #url = f"https://www.google.com/maps/search/?api=1&query={location.latitude},{location.longitude}"

        ## Open the URL in a web browser 
        #webbrowser.open(url)
        

    def pause_countdown(self):
        self.countdown_timer.stop()


    def update_countdown(self):
        self.T_MINUS += 1

        new_time = self.seconds_to_time_str(self.T_MINUS)

        self.countdown_label.setText(f"t {new_time}")

        if self.T_MINUS == 60 * 3:
            os.system("say 'Three minutes to launch.'")
        
        if self.T_MINUS == 60:
            os.system("say 'One minute to launch.'")

        if self.T_MINUS == 30:
            os.system("say 'Thirty seconds to launch.'")

        if self.T_MINUS == 0:
            os.system("say 'Ignition'")


    def edit_countdown(self):
        new_time = self.new_time.text()

        try:
            hours, minutes, seconds = new_time.split(':')
            self.T_MINUS = self.hours_minutes_seconds_to_seconds(int(hours), int(minutes), int(seconds))
            self.update_countdown()
        except:
            print(f"LAUNCH PROGRAM ERROR: Invalid time format: {new_time}. Please use the format HH:MM:SS")
        #self.countdown_label.setText(self.countdown)


    def seconds_to_time_str(self, seconds):
        hours = self.T_MINUS // 3600
        minutes = (self.T_MINUS % 3600) // 60
        seconds = self.T_MINUS % 60

        # Format the time as a string
        if seconds > 0:
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            time_str = f"-{hours:02}:{minutes:02}:{seconds:02}"

        return time_str
    

    #Move to functions.
    def hours_minutes_seconds_to_seconds(self, hours, minutes, seconds):
        
        return hours * 3600 + minutes * 60 + seconds
    

    def process_user_command(self):
        command = self.input.text()

        if command == "communication check" or command == "COMMUNICATION CHECK":
            if self.p1_read_serial_data.is_alive() == True:
                self.command_q.put(("PPPPP"))
                self.input.clear()
            else:
                send_single_command("PPPPP")
                self.input.clear()
    
        elif command == "launch imminent" or command == "LAUNCH IMMINENT":
            if self.p1_read_serial_data.is_alive() == True:
                self.command_q.put(("GGGGG"))
                self.input.clear()
            else:
                send_single_command("GGGGG")
                self.input.clear()

        elif command == "abort" or command == "ABORT":
            if self.p1_read_serial_data.is_alive() == True:
                self.command_q.put(("ABORT"))
                self.input.clear()
            else:
                send_single_command("ABORT")
                self.input.clear()

        elif command == "separate" or command == "SEPARATE":
            if self.p1_read_serial_data.is_alive() == True:
                self.command_q.put(("SSSSS"))
                self.input.clear()
            else:
                send_single_command("SSSSS")
                self.input.clear()

        elif command == "deploy main" or command == "DEPLOY MAIN":
            if self.p1_read_serial_data.is_alive() == True:
                self.command_q.put(("MMMMM"))
                self.input.clear()
            else:
                send_single_command("MMMMM")
                self.input.clear()
            
        else:
            print("\n LAUNCH PROGRAM ERROR: Invalid command for send_command function. Valid commands are: \n 'communication check' \n 'launch imminent' \n 'abort' \n")


    def set_up_labels_and_data_layout(self):
        self.start_button = QPushButton('Start Data Collection')
        self.start_button.clicked.connect(self.start_clicked)
        self.start_button.setCheckable(True)

        self.rocket_time_label = QLabel("Time, rocket: 0:00:00")
        self.rocket_time_label.setProperty("class", "data_label")
        self.ground_time_label = QLabel("Time, ground: 0:00:00")
        self.ground_time_label.setProperty("class", "data_label")
        #self.sync_time_button = QPushButton("Sync Rocket / Ground Time")
        #self.sync_time_button.clicked.connect(self.sync_rocket_and_ground_time)

        self.gps_coords = QLabel(f"GPS: 0.0000000, 0.0000000")
        self.gps_coords.setProperty("class", "data_label")

        self.gps_button = QPushButton("MAP")
        self.gps_button.clicked.connect(self.open_google_maps)


        self.temperature_label = QLabel("Outside temperature: ")
        self.temperature_label.setProperty("class", "data_label")
        self.gps_fix_label = QLabel("GPS Fix: ")
        self.gps_fix_label.setProperty("class", "data_label")

        self.phase_label = QLabel("Phase: ")
        self.phase_label.setProperty("class", "data_label")

        self.altitude_label = QLabel("Altitude: ")
        self.altitude_label.setProperty("class", "data_label")

        self.data_layout = QGridLayout()

        self.data_layout.addWidget(self.start_button, 0, 0, 1, 2)
        self.data_layout.addWidget(self.phase_label, 1, 0)
        self.data_layout.addWidget(self.altitude_label, 2, 0)
        self.data_layout.addWidget(self.rocket_time_label, 3, 0)
        self.data_layout.addWidget(self.ground_time_label, 4, 0)
        self.data_layout.addWidget(self.gps_coords, 5, 0)
        self.data_layout.addWidget(self.gps_button, 5, 1)
        self.data_layout.addWidget(self.gps_fix_label, 6, 0)
        self.data_layout.addWidget(self.temperature_label, 7, 0)

        self.data_layout.setColumnStretch(0, 3)
        self.data_layout.setColumnStretch(1, 1)


        self.main_layout.addLayout(self.data_layout, 0, 2, 4, 1)      # Add data layout to main layout.


    def select_program(self):
        """
        Selects appropriate program based on the PROGRAM variable. Program modes:

            1. Live data received through telemetry, write data to a csv file.
            2. Fake data generated in a process, writes data to a csv file.
            3. Visualize data from a csv file.
        """

        self.p1_read_serial_data = Process(target=serial_reader, args=(self.data_q, self.command_q))
        self.p2_write_to_csv_file = Process(target=csv_data_writer, args=(self.csv_queue,))
        #self.p3_countdown = Process(target=countdown, args=(self.countdown_q,))


    def start_clicked(self):

        if self.p1_read_serial_data.is_alive() == False:    # Might not be necessary to do this here. Not too important though.
            self.p1_read_serial_data.start()
            self.p2_write_to_csv_file.start()

        if self.START_CLICKED == False:
            self.timer.start()
            self.start_button.setText('Pause Data Collection')
            self.START_CLICKED = True

        else:
            self.timer.stop()
            self.start_button.setText('Start Data Collection')
            self.START_CLICKED = False


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


        else:
            print(f"LAUNCH PROGRAM ERROR: PLOT variable error detected. Plots will not be updated {datetime.now()}.")

            self.missed_packages_counter += 1

    
    # Open google maps to the current location based on the GPS coordinates.
    def open_google_maps(self):
        """
        Open google maps to the current location based on the GPS coordinates.
        """

        # Initialize geolocator
        self.geolocator = Nominatim(user_agent="my_app")

        # Build the initial URL with the latitude and longitude values
        url = f"https://www.google.com/maps/search/?api=1&query={self.gps_lat},{self.gps_long}"
        # Open the initial URL in a web browser and store the web browser instance
        self.browser = webbrowser.get()
        
        self.browser.open(url, new=2, autoraise=True)



    def update_gui(self):
        """
        Should update gui based on the data dictionary.
        """

        self.get_new_data()

        # BJØRN
        #self.rocket_mesh.rotate(angle=-self.rotation, x=self.axis[0], y=self.axis[1], z=self.axis[2])
        self.decode_and_calculations()
        #self.rot, self.axis = self.orientationQ.degrees, self.orientationQ.axis
        #self.rocket_mesh.rotate(angle=-self.rotation, x=self.axis[0], y=self.axis[1], z=self.axis[2])
        #print(self.orientationQ.angle)

        if len(self.data['t']) > 20:   # Need to get many data points for filtered values.
        
            if self.FIRST_TIME_MEASUREMENT == None:
                self.FIRST_TIME_MEASUREMENT = self.data['t'][-1]
                self.start_time = t.time()

            self.PLOT_COUNTER += 1

            if self.PLOT_COUNTER == self.REFRESH_RATE:

                end_time = t.time()
                elapsed_time = end_time - self.start_time

                rocketTime = str(timedelta(seconds=self.data['t'][-1]))
                groundTime = str(timedelta(seconds=elapsed_time + self.FIRST_TIME_MEASUREMENT))

                # Update plots
                self.plotline_alt.setData(self.data['t'][-200:], self.data['alt'][-200:])
                self.plotline_T_o.setData(self.data['t'][-200:], self.data['temp'][-200:])
                self.plotline_rssi.setData(self.data['t'][-200:], self.data['rssi'][-200:])
                self.plotline_a_x.setData(self.data['t'][-200:], self.data['a_x'][-200:])
                self.plotline_a_y.setData(self.data['t'][-200:], self.data['a_y'][-200:])
                self.plotline_a_z.setData(self.data['t'][-200:], self.data['a_z'][-200:])

                # Update labels
                self.rocket_time_label.setText(f"Time, rocket: {rocketTime:.7}")
                self.ground_time_label.setText(f"Time, ground: {groundTime:.7}")

                self.gps_lat = convert_gps_lat_coords(self.data['GPS_lat'][-1])
                self.gps_long = convert_gps_long_coords(self.data['GPS_long'][-1])
                gps = f"{self.gps_lat} N,   {self.gps_long} E"
                
                # Should delete the first element in the list if it is longer than 10 elements.
                if len(self.LAST_TEN_GPS) >= 10:
                    self.LAST_TEN_GPS.pop(0)

                self.gps_coords.setText(gps)
                self.LAST_TEN_GPS.append(gps)

                self.temperature_label.setText(f"Outside temperature: {self.data['temp'][-1]} °C")
                self.altitude_label.setText(f"Altitude: {self.data['alt'][-1]} m")

                self.gps_fix_label.setText(f"GPS fix: {self.data['GPS_fix'][-1] / 10}")
                #self.recovery_phase_label.setText(f"Recovery phase: {self.data['recovery_phase'][-1]}")

                self.PLOT_COUNTER = 0

        else:
            pass
    
    
    def user_closed(self):
        self.closeEvent(event=None)


    def closeEvent(self, event):
        self.p1_read_serial_data.terminate()
        self.p2_write_to_csv_file.terminate()


#####################################################################################
# BJØRN START

class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# BJØRN SLUTT
#####################################################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)   # Hardware acceleration for plots.

    with open("static/style/styles.css","r") as stylesheet:
        app.setStyleSheet(stylesheet.read())
        
    w = MainWindow()
    app.aboutToQuit.connect(w.user_closed)      # Prevents fuck-ups when closing plot.
    w.show()
    sys.exit(app.exec())