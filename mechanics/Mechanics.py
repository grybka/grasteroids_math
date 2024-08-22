from mechanics.Vector2D import Vector2D



class ExtendedBody2D:
    def __init__(self, position=Vector2D(0,0), velocity=Vector2D(0,0), mass=1, moment_of_inertia=1,angle=0,angular_velocity=0):
        super().__init__()
        self.mass = mass
        self.moment_of_inertia = moment_of_inertia
        self.position = position
        self.velocity = velocity        
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.force = Vector2D(0,0)
        self.torque=0        
        
    def get_mass(self):
        return self.mass
    
    def get_moment_of_inertia(self):
        return self.moment_of_inertia

    def get_position(self):
        return self.position
    
    def set_position(self, position):
        self.position = position

    def get_angle(self):
        return self.angle
    
    def set_angle(self, angle):
        self.angle = angle

    def get_velocity(self):
        return self.velocity
    
    def set_velocity(self, velocity):
        self.velocity = velocity

    def get_angular_velocity(self):
        return self.angular_velocity
    
    def set_angular_velocity(self, angular_velocity):
        self.angular_velocity = angular_velocity

    def apply_force(self, force, location):
        self.force += force
        self.apply_torque( (location-self.get_position()).cross(force) )

    def apply_torque(self, torque):
        self.torque += torque

    def update(self,dt):
        x0=self.get_position()
        v0=self.get_velocity()
        a=self.force/self.mass
        omega=self.get_angular_velocity()
        alpha=self.torque/self.moment_of_inertia
        self.set_position(x0+v0*dt+0.5*a*dt**2)
        self.set_velocity(v0+a*dt)
        self.set_angle(self.get_angle()+omega*dt+0.5*alpha*dt**2)        
        self.set_angular_velocity(omega+alpha*dt)
        self.force=Vector2D(0,0)
        self.torque=0

    def get_interaction_distance(self):
        return 0
    
class CircleBody2D(ExtendedBody2D):
    def __init__(self, radius=1,position=Vector2D(0,0), velocity=Vector2D(0,0), mass=1, moment_of_inertia=None,angle=0,angular_velocity=0):
        if moment_of_inertia is None: #solid circle
            moment_of_inertia=0.5*mass*radius**2
        super().__init__(position,velocity,mass,moment_of_inertia,angle,angular_velocity)
        self.radius=radius    

    def get_interaction_distance(self):
        return self.radius

class PolygonBody2D(ExtendedBody2D):
    def __init__(self, position=Vector2D(0,0), velocity=Vector2D(0,0), mass=1, moment_of_inertia=1,angle=0,angular_velocity=0,vertices=[]):
        super().__init__(position,velocity,mass,moment_of_inertia,angle,angular_velocity)
        self.vertices=vertices #vertices are relative to center
        self.get_interaction_distance=max([v.magnitude() for v in self.vertices])

    def get_edges(self): #get edge world coordinates.  List of [ (x1,y1), (x2,y2) ]
        edges=[]
        for i in range(len(self.vertices)):
            v1=self.vertices[i]
            v2=self.vertices[(i+1)%len(self.vertices)]
            edges.append( (self.get_position()+v1, self.get_position()+v2) )
        return edges

    def point_inside(self,x):
        #assume x is in the same coordinate system as the polygon
        #assume the polygon is convex
        #assume the vertices are in counterclockwise order
        for i in range(len(self.vertices)):
            v1=self.vertices[i]
            v2=self.vertices[(i+1)%len(self.vertices)]
            if (x-v1).cross(v2-v1)<0:
                return False
        return True
    

    def get_interaction_distance(self):
        return self.get_interaction_distance
    
class CompositeBody2D(ExtendedBody2D):
    def __init__(self):
        super().__init__()
        self.bodies=[]
        self.radius=0
        self.interaction_distance=0

    def add_body(self, body):
        self.bodies.append(body)
        self.recalculate_eveything()

    def recalculate_eveything(self):
        self.mass=sum([body.get_mass() for body in self.bodies])
        self.moment_of_inertia=0
        #center of mass
        x=Vector2D(0,0)
        for body in self.bodies:
            x+=body.get_position()*body.get_mass()
        self.position=x/self.mass
        #moment of inertia
        for body in self.bodies:
            #Ahh, the parallel axis theorem
            self.moment_of_inertia+=body.get_moment_of_inertia()+body.get_mass()*(body.get_position()-self.position).magnitude_squared()
        #interaction distance        
        for body in self.bodies:
            interaction_distance=(body.get_position()-self.get_position()).magnitude()+body.get_interaction_distance()
            if interaction_distance>self.interaction_distance:
                self.interaction_distance=interaction_distance

    #assume I want to move the cm
    def set_position(self, position):        
        offset=position-self.get_position()
        for body in self.bodies:
            body.set_position(body.get_position()+offset)
        super().set_position(position)

    def set_angle(self, angle):
        offset=angle-self.get_angle()
        for body in self.bodies:
            body.set_position(self.get_position()+(body.get_position()-self.get_position()).rotated_by(offset))
            body.set_angle(body.get_angle()+offset)
        super().set_angle(angle)

    def get_interaction_distance(self):
        return self.interaction_distance
    
def get_contacts_poly_poly(body1, body2):
    return []

def get_contacts_poly_circle(poly, circle):
    edges=poly.get_edges()
    contacts=[]
    for edge in edges:
        edgevec=edge[1]-edge[0]
        normal=Vector2D(-edgevec.y,edgevec.x).normalized()
        distance=(circle.get_position()-edge[0]).dot(normal)
        if distance>circle.radius:
            continue
        

        

    return []

#get contacts between two bodies
#response is list of [contact_point, normal, penetration]
def get_contacts(body1, body2):
    dx=body2.get_position()-body1.get_position()

    if dx.magnitude()>=body1.get_interaction_distance()+body2.get_interaction_distance():
        return []
    #print("close contact")
    if isinstance(body1, CircleBody2D) and isinstance(body2, CircleBody2D):        
        distance=dx.magnitude()
        penetration=body1.radius+body2.radius-distance
        if penetration<=0:
            return []
        norm=dx.normalized()
        contact_point=body1.get_position()+(body1.radius-0.5*penetration)*norm
        return [ (contact_point,norm,penetration) ]                    
    if isinstance(body1, CircleBody2D) and isinstance(body2, PolygonBody2D):        
        return get_contacts_poly_circle(body2,body1)
    if isinstance(body1, PolygonBody2D) and isinstance(body2, CircleBody2D):
        return get_contacts_poly_circle(body1,body2)
    if isinstance(body1, PolygonBody2D) and isinstance(body2, PolygonBody2D):
        return get_contacts_poly_poly(body1,body2)
    elif isinstance(body1, CompositeBody2D):
        contacts=[]
        for body in body1.bodies:
            contacts+=get_contacts(body, body2)
        return contacts
    elif isinstance(body2, CompositeBody2D):
        contacts=[]
        for body in body2.bodies:
            contacts+=get_contacts(body1, body)
        return contacts