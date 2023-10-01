import serial
from serial import *
import numpy as np
import serial.tools.list_ports
import time as t

INT8 = (np.int8, 1)
UINT8 = (np.uint8, 1)
INT16 = (np.int16, 2)
UINT16 = (np.uint16, 2)
INT32 = (np.int32, 4)
UINT32 = (np.uint32, 4)
FLOAT = (np.single, 4)
DOUBLE = (np.double, 8)

# INPUTS:
# <byte_arr>: bytes-objekt fra python som inneholder x antall bytes sendt over USART
# <dtype_list>: liste over hvilke datatyper tallene som blir sendt har
# OUTPUT:
# ...en liste med tall
def decode_bytearray(byte_arr, dtype_list):
    offset = 0  # teller som bestemmer hvilke bytes som skal leses fra arrayet i hver iterasjon
    data_list = []  # output
    for dtype, nbytes in dtype_list:  # gå gjennom hvert datapunkt som skal leses ifølge predefinert liste
        # hent ut definert antall bytes fra posisjon definert av os og dekod fra datatype definert i liste
        # indeks [0] på slutten for å få bare tallet og ikke en numpyarray
        data_list.append(np.frombuffer(byte_arr, dtype=dtype, count=1, offset=offset)[0])
        offset += nbytes  # inkrementer os til neste posisjon for byte som skal leses
    return data_list


#def adjust_time(raw_time, time_counter, initial_offset=0, Ts=0.01):  # hvis tid sendes som uint8: max-verdi = 255, Ts=0.01 gir samplefrekvens 100 Hz
#    out = (raw_time - initial_offset + 256*time_counter)*Ts          # må endres hvis vi sender tid med annet format eller har variabel samplefrekvens
#    if raw_time == 255:                                              # initial_offset kan lagres som første tidsmåling som kommer inn for at telling skal starte som null
#        time_counter += 1
#    return out, time_counter


def detect_serial_port():
    """
    Detects the serial port that the Ground station is connected to.
    """
    ports = list(serial.tools.list_ports.grep('usbserial'))
    
    for p in ports:
        if len(p.device) == 26:
            serial_port = p.device
            serial_port.replace("cu", "tty")
            print(f"\n Serial port {p.device} selected. \n")
            return serial_port
        

def send_single_command(command):
    """
    Sends a single command to the outgoing ground station.
    """
    serial_port = detect_serial_port()
    ser = serial.Serial(serial_port, 115200)
    ser.write(command.encode())
    ser.close()
    print(f"COMMAND {command} IS VALID. COMMAND WRITTEN TO GROUND STATION.")


def serial_reader(queue, command_queue):

    """
    Should read and decode data from serial port.

    """
    print("LAUNCH PROGRAM: Serial process is go.")    # Tell user that the process has started.

    serial_port = detect_serial_port()
    ser = serial.Serial(serial_port, 115200)

    data_type_list = [

            UINT32,     # Counter
            UINT8,      # Plot-indicator

            FLOAT,      # Akselerometer X
            FLOAT,      # Akselerometer Y
            FLOAT,      # Akselerometer Z
            FLOAT,      # Magnetometer X
            FLOAT,      # Magnetometer Y
            FLOAT,      # Magnetometer Z
            FLOAT,      # Gyroskop X
            FLOAT,      # Gyroskop Y
            FLOAT,      # Gyroskop Z
            FLOAT,      # GPS Latitude
            FLOAT,      # GPS Longitude
            UINT16,     # Altitude[m]
            INT16,      # Temperatur (°C * 10)
            UINT16,     # Trykk (mBar)
            UINT8,      # GPS Fix (binary)
            UINT8,      # Recovery phase indication
            UINT16,     # Recovery status
            FLOAT,      # Estimated angle

            INT8,       # RSSI
            INT8        # SNR
            
            ]
    
    aa_counter = 0

    while True:

        while True:
            first_bytes = ser.read(1)   # Read first 4 bytes to check if they are the start bytes.

            if first_bytes == b'\xaa':
                aa_counter += 1
            else:
                aa_counter = 0

            if aa_counter == 4:
                break

        serial_data = ser.read(65)
        data = decode_bytearray(serial_data,  data_type_list)
        queue.put((*data,))

        try:
            command = command_queue.get_nowait()
            ser.write(command.encode())
            print(f"LAUNCH PROGRAM MESSAGE: COMMAND {command} SENT TO SERIAL PORT")
        
        except:
            pass