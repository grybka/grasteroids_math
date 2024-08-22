import math

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y    

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def __neg__(self):
        return Vector2D(-self.x, -self.y)
    
    def __getitem__(self, key):
        return self.x if key == 0 else self.y
    
    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        else:
            self.y = value

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        return "({},{})".format(self.x, self.y)
    
    def rotated_by(self, angle):        
        return Vector2D(self.x * math.cos(angle) - self.y * math.sin(angle), self.x * math.sin(angle) + self.y * math.cos(angle))
    
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def magnitude_squared(self):
        return self.x ** 2 + self.y ** 2
    
    def length(self):
        return self.magnitude()
    
    def copy(self):
        return Vector2D(self.x, self.y)
    
    def normalized(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return self / mag    
    
    def to_tuple(self):
        return (self.x, self.y)
    
    def to_int_tuple(self):
        return (int(self.x), int(self.y))
    
#returns the distance between a point and an infinite line
#positive is to the right, negative to the left
def point_distance_to_line(line,point):
    line_right_normal=Vector2D(-line[1].y,line[1].x).normalized()
    return (point-line[0]).dot(line_right_normal)

#returns the fractional distance along a line that is closest to a point
def closest_point_on_line_fractional(line,point):
    lamda=(point-line[0]).dot(line[1]-line[0])/(line[1]-line[0]).magnitude_squared()
    if lamda<0:
        return 0
    if lamda>1:
        return 1
    return lamda