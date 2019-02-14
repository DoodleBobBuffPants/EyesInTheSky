from threading import Thread
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from backend import movement
from frontend import MediaPlayer

app = Flask(__name__)

app.secret_key = b'\xe7q\xb6j\xac\xbe!\xc77\x95%\xe2\x1eV\xfcD\xfce\xe8O\xde\x17\xf3\xd1'

# Global-ish drone variable, this will only work when the server runs on a single thread and there is one user
# sending requests TODO: change this so it is better
# This also connects to the drone as soon as the server starts
# TODO: might be better to have a separate connect button on interface ???

drone = movement.FollowingDrone(num_retries=10)  # Create a single drone object on server


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
    follow_thread.start()
    # follow_thread2 = Thread(target=drone.slowdown, args=[0.01, 2])
    # follow_thread2.start()
    return jsonify({})


@app.route('/video_start', methods=['POST'])
def video():
    drone.set_video_resolutions("rec1080_stream480")
    drone.set_video_framerate("24_FPS")

    # start video stream as separate process as it is blocking
    vidPath = "frontend/bebop.sdp"
    streamProc = Thread(target=MediaPlayer.playVid, args=[vidPath, drone])
    streamProc.start()
    return jsonify({})


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


if __name__ == "__main__":
    app.run()