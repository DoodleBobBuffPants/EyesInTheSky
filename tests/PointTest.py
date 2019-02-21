# test point
import backend.Point as Point
from threading import Thread

def prod(point):
    for i in range(9):
        point.set(i, i)

def cons(point):
    for i in range(9):
        print(point.get())

point = Point.Point()
pro = Thread(target=prod, args=[point])
con = Thread(target=cons, args=[point])
pro.start()
con.start()