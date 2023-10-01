from flask import Flask, render_template, request, make_response
import json

# http://localhost:5000/

# Import dependencies
from py.commands import CommandHandler
from py.datamng import DataManager
from py.orientation import OrientationService
from py.gps import GPS
from py.phases import get_phase,next_phase
from py.telemetry import TelemetryService
import py.csv_data_writer as csv_data_writer

from py.csv_data_writer import csv_data_writer
from py.serial_reader import serial_reader, send_single_command

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Set up dependencies
comhdl = CommandHandler()
datamng = DataManager()
rot = OrientationService()
gps = GPS()
tlmsrv = TelemetryService(serial_reader,csv_data_writer)
tlmsrv.try_connect()

#region templates -----------------------------------------
@app.route("/")
def ROUTE_index():
    return render_template('index.html')
#endregion ------------------------------------------------

#region api endpoints -------------------------------------
# Phase
@app.route("/api/phase", methods=["GET"])
def api_get_phase(): return get_phase()

@app.route("/api/phase", methods=["POST"])
def api_next_phase(): return next_phase()

@app.route("/api/fire")
def api_countdown_fire():
    #
    # DO SOME STUFF HERE
    #
    return next_phase()

# Commands
@app.route("/api/command", methods=["POST"])
def api_exec_command():
    data = request.get_json()
    com = data['command']
    val, err = comhdl.execute(com,tlmsrv)
    return json.dumps({"err":err,"value":val})

@app.route("/api/command", methods=["GET"])
def api_get_commands():
    if comhdl:
        return json.dumps(comhdl.commands)
    return json.dumps({"err":"Could not retrieve commands."})

# GPS
@app.route("/api/gps", methods=["GET"])
def api_get_gps():
    if gps and gps.alive:
        coords=gps.get_coordinates()
        return make_response(json.dumps(coords),200)
    return make_response(json.dumps({"err":"GPS failed."}),400)

# Orientation
@app.route("/api/orientation/<xyz>", methods=["GET"])
def api_orientation(xyz):
    xyz = xyz.lower()
    o = rot.euler_angles()
    response={}
    if "x" in xyz: response['x']=o[0]
    if "y" in xyz: response['y']=o[1]
    if "z" in xyz: response['z']=o[2]
        
    return json.dumps(response)

# Status
@app.route("/api/status", methods=["GET"])
def api_status(): return json.dumps(tlmsrv.status)

#endregion ------------------------------------------------

if __name__ == "__main__":
    import threading
    import time
    print("starting...")
    def run():
        while True:
            time.sleep(0.2)
            continue
    mainthread = threading.Thread(target=run)
    #mainthread.start() # no need to join, runs forever
    
    app.run(debug=True)