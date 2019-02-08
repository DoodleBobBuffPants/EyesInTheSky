from threading import Thread

from flask import Flask, render_template, request, redirect, url_for, flash

from backend import movement

app = Flask(__name__)

# TODO: INSECURE, change this to get from a hidden config file
app.secret_key = b'\xe7q\xb6j\xac\xbe!\xc77\x95%\xe2\x1eV\xfcD\xfce\xe8O\xde\x17\xf3\xd1'

# Global-ish drone variable, this will only work when the server runs on a single thread and there is one user
# sending requests TODO: change this so it is better
# This also connects to the drone as soon as the server starts
# TODO: might be better to have a separate connect button on interface ???
drone = movement.FollowingDrone()  # Create a single drone object on server


@app.route('/')
def home():
    return render_template('tester.html')


@app.route('/change_rel_coords', methods=['POST'])
def change():
    try:
        x = request.form["new_x"]
        y = request.form["new_y"]

        print(x, y)
        drone.car_rel_x = float(x)
        drone.car_rel_y = float(y)
    except Exception as e:
        print(str(e))
        flash(str(e))
    return redirect(url_for('home'))


@app.route('/takeoff', methods=['POST'])
def takeoff():
    drone.takeoff()
    return redirect(url_for('home'))


@app.route('/abort', methods=['POST'])
def stop_it():
    """ Lands drone in emergency, doesn't disconnect"""
    drone.immediate_land()
    return redirect(url_for('home'))


@app.route('/connect', methods=['POST'])
def connect():
    if not drone.connected:
        drone.connect(10)
    return redirect(url_for('home'))


@app.route('/disconnect', methods=['POST'])
def disconnect():
    if drone.connected:
        drone.disconnect()
    return redirect(url_for('home'))


@app.route('/follow', methods=['POST'])
def follow():
    try:
        if drone is None:
            flash("No drone yet")
        drone.stop_following = False
        follow_thread = Thread(target=drone.follow_car, args=[])
        follow_thread.start()
        follow_thread2 = Thread(target=drone.slowdown, args=[0.01, 2])
        follow_thread2.start()

    except Exception as e:
        flash(str(e))
    finally:
        return redirect(url_for('home'))


@app.route('/follow_stop', methods=['POST'])
def follow_stop():
    """Stops drone to a still hover, doesn't disconnect or land"""
    drone.stop_following = True
    drone.hover()

    # Find a way to kill the follow thread ??
    # Or maybe setting flag is sufficient
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()
