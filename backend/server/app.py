from threading import Thread

import flask
from flask import Flask, render_template, request, g, redirect, abort

from backend import movement

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('tester.html')


@app.route('/change_rel_coords', methods=['POST'])
def change():
    drone = get_drone()
    x = request.form["new_x"]
    y = request.form["new_y"]

    drone.car_rel_x = x
    drone.car_rel_y = y
    return redirect('/')


@app.route('/takeoff', methods=['POST'])
def takeoff():
    get_drone()
    return redirect('/')


@app.route('/abort', methods=['POST'])
def stop_it():
    stop_drone()
    return redirect('/')


@app.route('/follow', methods=['POST'])
def follow():
    if g.drone is None:
        abort(400, "no drone yet")

    g.follow_thread = Thread(target=g.drone.follow_car, args=[])
    g.follow_thread.start()


@app.route('/follow_stop', methods=['POST'])
def follow_stop():
    if g.drone is None:
        abort(400, "no drone yet")
    elif g.follow_thread is None:
        abort(400, "not following")

    stop_drone()
    # Find a way to kill the follow thread or change its variables


def get_drone():  # WARNING: This will also cause the drone to TAKE OFF
    drone = getattr(g, 'drone', None)
    if drone is None:
        drone = g.drone = movement.Drone()
    return drone


def stop_drone():
    drone = getattr(g, 'drone', None)
    if drone is not None:
        drone.immediate_land()
        drone.teardown()


@app.teardown_appcontext
def close_drone(exception):
    stop_drone()


if __name__ == "__main__":
    app.run()
