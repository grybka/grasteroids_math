from pymunk import Vec2d
from sprites.Sprite import *
from engine.GameObjects import *
from engine.Sound import *

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
        self.sound_on=False #true if it should play a sound when on

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
            if self.sound_on:
                get_sound_store().get_channel("engine").set_volume(0.5*self.throttle)
                get_sound_store().get_channel("engine").unpause()                
                print("sound unpau sed throttle {}".format(self.throttle))
        else:
            if self.sound_on:
                get_sound_store().get_channel("engine").pause()

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
    
    def get_expected_angular_acceleration(self,ship):
        return self.throttle*self.max_torque/ship.body.moment

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
        attachment_side=kwargs.pop("attachment_side")
        attachment_front=kwargs.pop("attachment_front")
        attachment_back=kwargs.pop("attachment_back")
        direction=kwargs.pop("direction",None)
        ShipPart.__init__(self,Vec2d(0,0))        
        self.thruster_2=Thruster(attachment=Vec2d(0,-attachment_back),direction=Vec2d(0,1),**kwargs)        
        self.thruster_1=Thruster(attachment=Vec2d(0,attachment_front),direction=Vec2d(0,-1),**kwargs)        
        self.thruster_3=Thruster(attachment=Vec2d(-attachment_side,0),direction=Vec2d(1,0),**kwargs)        
        self.thruster_4=Thruster(attachment=Vec2d(attachment_side,0),direction=Vec2d(-1,0),**kwargs)

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



class Cannon(ShipPart):
    def __init__(self,attachment=Vec2d(0,0),cooldown=0.2,projectile_speed=300,projectile_radius=2,projectile_color=(0,255,0),direction=Vec2d(0,1)):
        self.attachment=attachment
        self.cooldown=cooldown
        self.time_since_last_shot=0
        self.projectile_speed=projectile_speed
        self.projectile_radius=projectile_radius
        self.projectile_color=projectile_color
        self.firing=False
        self.direction=direction

    def fire(self):
        self.firing=True

    def update(self,ticks,engine,ship):
        self.time_since_last_shot+=ticks/1000
        if self.firing and self.time_since_last_shot>self.cooldown:
            get_sound_store().play_sound("laser")
            self.time_since_last_shot=0            
            projectile=Bullet(radius=self.projectile_radius,color=self.projectile_color)
            projectile.set_position(ship.body.position+self.attachment.rotated(ship.body.angle))
            projectile.set_angle(ship.body.angle)
            projectile.set_velocity(ship.body.velocity+self.direction.rotated(ship.body.angle)*self.projectile_speed)            
            engine.schedule_add_object(projectile)            
            #make_space_explosion(engine,object.position,particle_count=100,particle_lifetime=1,mean_particle_speed=100,particle_speed_sigma=10,particle_radius=2,particle_color=(255,255,255),explosion_velocity=object.velocity+self.direction.rotated_by(object.rotation)*self.projectile_speed)
            #TODO add sound effect here
            #self.firing=False

class LaserCannon(ShipPart):
    def __init__(self,attachment=Vec2d(0,0),cooldown=0.2,projectile_speed=600,direction=Vec2d(0,1)):
        self.attachment=attachment
        self.cooldown=cooldown
        self.time_since_last_shot=0
        self.projectile_speed=projectile_speed
        self.firing=False
        self.direction=direction

    def fire(self):
        self.firing=True

    def update(self,ticks,engine,ship):
        self.time_since_last_shot+=ticks/1000
        if self.firing and self.time_since_last_shot>self.cooldown:
            self.time_since_last_shot=0            
            start_pos=ship.body.position+self.attachment.rotated(ship.body.angle)
            projectile=LaserBeam(start_position=start_pos)            
            projectile.set_velocity(ship.body.velocity+self.direction.rotated(ship.body.angle)*self.projectile_speed)            
            projectile.set_angle(ship.body.angle)
            engine.schedule_add_object(projectile)            
            #make_space_explosion(engine,object.position,particle_count=100,particle_lifetime=1,mean_particle_speed=100,particle_speed_sigma=10,particle_radius=2,particle_color=(255,255,255),explosion_velocity=object.velocity+self.direction.rotated_by(object.rotation)*self.projectile_speed)
            #TODO add sound effect here
            #self.firing=False


