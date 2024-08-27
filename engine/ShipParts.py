from pymunk import Vec2d
from sprites.Sprite import *
from engine.GameObjects import *

class ShipPart:
    def __init__(self,attachement=Vec2d(0,0)):
        self.attachment=attachement

    def get_attachment(self):
        return self.attachment
    
    def update(self,ticks,engine,ship):
        pass

class Thruster(ShipPart):
    def __init__(self,**kwargs):
        defaultKwargs={"max_force":100,"attachment":Vec2d(0,0),"direction":Vec2d(0,1),"thrust_color":(255,255,0),"thrust_particle_size":10,"thrust_particle_speed":100,"thrust_particle_period":0.1}
        kwargs = { **defaultKwargs, **kwargs }
        ShipPart.__init__(self,kwargs["attachment"])
        self.throttle=0
        self.max_force=kwargs["max_force"]
        self.direction=kwargs["direction"] #direction that the thruster points in
        #regarding thrust particles
        self.time_since_last_thrust_particle=0
        self.thrust_particle_period=kwargs["thrust_particle_period"]
        self.thrust_particle_speed=kwargs["thrust_particle_speed"]
        self.thrust_particle_size=kwargs["thrust_particle_size"]
        self.thrust_color=kwargs["thrust_color"]

    def set_throttle(self,throttle): #throttle is a float from 0 to 1
        self.throttle=throttle
        if self.throttle>1:
            self.throttle=1
        if self.throttle<0:
            self.throttle=0
        #print("throttle set to ",self.throttle)


    def update(self,ticks,engine,ship):
        if self.throttle>0:
            total_force=self.throttle*self.max_force*self.direction
            ship.body.apply_force_at_local_point(total_force,self.attachment)
            #thrust particles
            if self.time_since_last_thrust_particle>self.thrust_particle_period:        
                self.time_since_last_thrust_particle=0
                particle=ThrustDecorator(max_radius=self.thrust_particle_size*self.throttle,color=self.thrust_color)
                particle.set_position(ship.body.position+self.attachment.rotated(ship.body.angle))
                particle.set_velocity(ship.body.velocity-self.direction.rotated(ship.body.angle)*self.thrust_particle_speed)
                engine.add_decorator(particle)
            else:
                self.time_since_last_thrust_particle+=ticks/1000

class ReactionWheel(ShipPart):
    def __init__(self,max_torque=100):
        ShipPart.__init__(self)
        self.max_torque=max_torque
        self.throttle=0
        self.max_angular_velocity=3

    def set_throttle(self,throttle): #throttle is a float from -1 to 1
        if throttle>1:
            throttle=1
        if throttle<-1:
            throttle=-1
        self.throttle=throttle    

    def update(self,ticks,engine,ship):
        if self.throttle!=0:
            total_torque=self.throttle*self.max_torque
            if ship.body.angular_velocity>self.max_angular_velocity and total_torque>0:
                total_torque=0
            elif ship.body.angular_velocity<-self.max_angular_velocity and total_torque<0:
                total_torque=0
            ship.body.torque+=total_torque
    
class ManeuverThruster(ShipPart):
    def __init__(self,**kwargs):
        self.attachment=(0,0)        
        attachment=kwargs.pop("attachment")
        direction=kwargs.pop("direction",None)
        ShipPart.__init__(self,Vec2d(0,0))        
        self.thruster_2=Thruster(attachment=Vec2d(0,-attachment[1]),direction=Vec2d(0,1),**kwargs)        
        self.thruster_1=Thruster(attachment=Vec2d(0,attachment[1]),direction=Vec2d(0,-1),**kwargs)        
        self.thruster_3=Thruster(attachment=Vec2d(-attachment[0],0),direction=Vec2d(1,0),**kwargs)        
        self.thruster_4=Thruster(attachment=Vec2d(attachment[0],0),direction=Vec2d(-1,0),**kwargs)

    def set_throttle_ns(self,throttle): #throttle between -1 and 1
        if throttle>0:
            self.thruster_2.set_throttle(throttle)
            self.thruster_1.set_throttle(0)
        else:
            self.thruster_2.set_throttle(0)
            self.thruster_1.set_throttle(-throttle)        

    def set_throttle_ew(self,throttle): #throttle between -1 and 1
        if throttle>0:
            self.thruster_4.set_throttle(throttle)
            self.thruster_3.set_throttle(0)
        else:
            self.thruster_4.set_throttle(0)
            self.thruster_3.set_throttle(-throttle)          

    def update(self,ticks,engine,object):
        self.thruster_1.update(ticks,engine,object)
        self.thruster_2.update(ticks,engine,object)
        self.thruster_3.update(ticks,engine,object)
        self.thruster_4.update(ticks,engine,object)


