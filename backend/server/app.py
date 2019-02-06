from flask import Flask, render_template, request, g, redirect

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
def abort():
    stop_drone()
    return redirect('/')


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
