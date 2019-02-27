from backend.Camera import DroneCamera
from backend.FindRed import find_red

from threading import Thread
from flask import Flask, render_template, request, jsonify, Response
from backend import movement, FindRed
from frontend import MediaPlayer

import cv2
import os

os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'protocol_whitelist;file,rtp,udp'

app = Flask(__name__)

# media player object for new thread
mp = MediaPlayer.MediaPlayer()

app.secret_key = b'\xe7q\xb6j\xac\xbe!\xc77\x95%\xe2\x1eV\xfcD\xfce\xe8O\xde\x17\xf3\xd1'

# Global-ish drone variable, this will only work when the server runs on a single thread and there is one user
# sending requests TODO: change this so it is better
# This also connects to the drone as soon as the server starts
# TODO: might be better to have a separate connect button on interface ???

# Create a single drone object on server
drone = movement.FollowingDrone(num_retries=10)
c = DroneCamera(drone)


@app.route('/')
def home():
    return render_template('tester.html')


@app.route('/change_rel_coords', methods=['POST'])
def change():
    x = request.json["new_x"]
    y = request.json["new_y"]
    drone.car_rel_x = float(x)
    drone.car_rel_y = float(y)
    return jsonify({})


@app.route('/takeoff', methods=['POST'])
def takeoff():
    if not (drone.connected or drone.drone_connection.is_connected):
        return jsonify(message="Drone not Connected"), 500
    return jsonify(command_sent=drone.atakeoff())


@app.route('/abort', methods=['POST'])
def stop_it():
    """ Lands drone in emergency, doesn't disconnect"""
    drone.immediate_land()
    return jsonify({})


@app.route('/connect', methods=['POST'])
def connect():
    if drone.connected or drone.drone_connection.is_connected:
        return jsonify(message="Drone already connected"), 500
    return jsonify(connected=drone.connect(10))


@app.route('/disconnect', methods=['POST'])
def disconnect():
    if drone.connected:
        drone.disconnect()
        drone.connected = False
    return jsonify({})


@app.route('/follow', methods=['POST'])
def follow():
    drone.stop_following = False
    follow_thread = Thread(target=drone.follow_car, args=[])
    follow_thread.daemon = True
    follow_thread.start()

    return jsonify({})


def get_coords(frame):
    x, y = find_red(frame)
    return x, y


def gen(cam: DroneCamera):
    while True:
        frame = cam.get_frame()
        if frame is not None:
            ret, jpgframe = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpgframe.tobytes() + b'\r\n')


@app.route('/video_experiment')
def vid():
    return render_template('vid.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen(c),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed1')
def video_feed1():
    return Response(gen(c), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/battery', methods=['POST'])
def battery():
    return jsonify({"battery": "100"})


@app.route('/stop_follow', methods=['POST'])
def follow_stop():
    """Stops drone to a still hover, doesn't disconnect or land"""
    drone.stop_following = True
    drone.hover()

    # Find a way to kill the follow thread ??
    # Or maybe setting flag is sufficient
    return jsonify({})


@app.errorhandler(Exception)
def errors(err: Exception):
    response = jsonify(message=str(err),
                       status_code=500)
    return response, 500


# can get a reference to the frame.jpg lock
def getFrameLock():
    return mp.getLock()


if __name__ == "__main__":
    app.run()
