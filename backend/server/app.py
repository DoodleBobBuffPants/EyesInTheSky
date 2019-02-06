from threading import Thread

from flask import Flask, render_template, request, redirect, abort

from backend import movement

app = Flask(__name__)

# Global-ish drone variable, this will only work when the server runs on a single thread and there is one user
# sending requests TODO: change this so it is better
# This also connects to the drone as soon as the server starts
# TODO: might be better to have a separate connect button on interface ???
drone = movement.Drone()  # Create a single drone object on server


@app.route('/')
def hello_world():
    return render_template('tester.html')


@app.route('/change_rel_coords', methods=['POST'])
def change():
    if drone:
        x = request.form["new_x"]
        y = request.form["new_y"]

        drone.car_rel_x = x
        drone.car_rel_y = y
        return redirect('/')
    else:
        return abort(400, "No drone yet")


@app.route('/takeoff', methods=['POST'])
def takeoff():
    drone.takeoff()
    return redirect('/')


@app.route('/abort', methods=['POST'])
def stop_it():
    """ Lands drone in emergency, doesn't disconnect"""
    # drone.immediate_land()
    drone.drone.safe_land(5)
    return redirect('/')


@app.route('/connect', methods=['POST'])
def connect():
    if not drone.connected:
        drone.drone.connect(10)
    return redirect('/')


@app.route('/disconnect', methods=['POST'])
def disconnect():
    if drone.connected:
        drone.drone.disconnect()
    return redirect('/')


@app.route('/follow', methods=['POST'])
def follow():
    if drone is None:
        abort(400, "no drone yet")

    follow_thread = Thread(target=drone.follow_car, args=[])
    follow_thread.start()


@app.route('/follow_stop', methods=['POST'])
def follow_stop():
    if drone is None:
        abort(400, "no drone yet")

    if drone is not None:
        drone.stop_flight = True
        drone.immediate_land()  # Land drone, but stay connected

    # Find a way to kill the follow thread ??


if __name__ == "__main__":
    app.run()
