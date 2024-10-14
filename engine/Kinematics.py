from pymunk import Vec2d

#Given an initial 2d position x0, initial velocity v0, and maximum acceleration amax, calculate the optimal acceleration a_x, a_y that minimizes the time to reach target position x1
def calculate_intercept_acceleration(x0: Vec2d,v0: Vec2d,amax, x1: Vec2d):
    dx=x1-x0
    #TODO

