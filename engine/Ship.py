from engine.GameObjects import *
from pymunk import Vec2d
from sprites.Sprite import *    
from sprites.SpriteSheet import get_sprite_store
from engine.ShipParts import *
from enum import Enum
from engine.Magnetile import *
import random

class PointingNavigationMode(Enum):
    MANUAL=1
    SET_DIRECTION=2
    ZERO_ANGULAR_VELOCITY=3

class VelocityNavigationMode(Enum):
    MANUAL=1
    SET_VELOCITY=2
    SET_THRUST=3

class MagnetileShip(MagnetileConstruction):
    def __init__(self,position=Vec2d(0,0),shape_fname=None):  

        MagnetileConstruction.__init__(self,shape_fname=shape_fname)                 
        bbox=self.get_bbox()
        self.bbox=bbox
      
        #parts
        self.ship_parts=[]
        self.thruster=Thruster(attachment=Vec2d(0,bbox[1]),max_force=1e4)
        self.ship_parts.append(self.thruster)
        self.reaction_wheel=ReactionWheel(max_torque=2e5)
        self.ship_parts.append(self.reaction_wheel)
        self.maneuver_thruster=ManeuverThruster(attachment_front=bbox[3],attachment_side=abs(bbox[0]),attachment_back=abs(bbox[1]),max_force=2e3,thrust_color=(128,128,128),thrust_particle_size=5)
        self.ship_parts.append(self.maneuver_thruster)
        self.cannon=Cannon(attachment=Vec2d(0,bbox[3]))
        self.ship_parts.append(self.cannon)
        #self.cannon=LaserCannon(attachment=Vec2d(0,bbox[3]))
        #self.ship_parts.append(self.cannon)
        #navigation
        #self.navigation_mode=NavigationMode.MANUAL
        self.desired_direciton=Vec2d(0,1)
        self.desired_velocity=Vec2d(0,0)
        self.desired_thrust=Vec2d(0,0)
        self.inertial_dampening=2e-3
        self.pointing_navigation_mode=PointingNavigationMode.MANUAL
        self.velocity_navigation_mode=VelocityNavigationMode.MANUAL

        #game stats
        self.max_health=10
        self.health=10
        self.max_shields=10
        self.shields=10
        self.reactor_breach=False

    def update(self,ticks,engine):
        self.update_navigation()
        self.body.velocity=self.body.velocity*(1-self.inertial_dampening)
        GameObject.update(self,ticks,engine)
        for part in self.ship_parts:
            part.update(ticks,engine,self)  
        if self.reactor_breach:
            self.explode(engine)      

    def get_shields(self):
        #returns a number and a maxnumber for drawing bars
        return self.shields,self.max_shields
    
    def get_health(self):
        #returns a number and a maxnumber for drawing bars
        return self.health,self.max_health
    
    def do_damage(self,damage):
        if self.shields>0:
            self.shields-=damage
            if self.shields<0:
                self.health+=self.shields
                self.shields=0
        else:
            self.health-=damage
        if self.health<=0:
            self.reactor_breach=True

    def set_desired_direction(self,direction):
        self.desired_direciton=direction

    def set_pointing_navigation_mode(self,mode):
        self.pointing_navigation_mode=mode

    def set_velocity_navigation_mode(self,mode):
        self.velocity_navigation_mode=mode
    
    def set_desired_velocity(self,velocity):
        self.desired_velocity=velocity

    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direciton.x,self.desired_direciton.y)    
        delta_angle=desired_angle-self.body.angle
        while delta_angle>math.pi:
            delta_angle-=2*math.pi
        while delta_angle<-math.pi:
            delta_angle+=2*math.pi

        def sign(x):
            if x>0:
                return 1
            return -1
        dead_angle=0.2     
        x=delta_angle
        v=self.body.angular_velocity
        a=self.reaction_wheel.get_expected_angular_acceleration(self)        
        dt=1/60
        
        if abs(2*a*x)<=v*v and sign(x)*sign(v)>0: #if we can't stop in time
            throttle=-1*sign(x)
        else:
            throttle=1*sign(x)
        
        self.reaction_wheel.set_throttle(throttle)

    def navigation_zero_angluar_velocity(self):
        #print("zeroing angular velocity")
        self.reaction_wheel.set_throttle(-10*self.body.angular_velocity)
        

    """
    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direciton.x,self.desired_direciton.y)    
        delta_angle=desired_angle-self.body.angle
        while delta_angle>math.pi:
            delta_angle-=2*math.pi
        while delta_angle<-math.pi:
            delta_angle+=2*math.pi
        pid_p=100
        pid_v=50
        dead_angle=0.1
        if abs(delta_angle)>dead_angle:
            throttle=delta_angle*pid_p-self.body.angular_velocity*pid_v
            self.reaction_wheel.set_throttle(throttle)
        else:
            throttle=-self.body.angular_velocity*pid_v
            self.reaction_wheel.set_throttle(throttle) """

    def navigation_set_velocity(self):
        dead_velocity=0.1
        ew_dir=Vec2d(1,0).rotated(self.body.angle)
        ns_dir=Vec2d(0,1).rotated(self.body.angle)
        delta_v=self.desired_velocity-self.body.velocity
        if delta_v.length<dead_velocity:
            self.maneuver_thruster.set_throttle_ns(0)
            self.maneuver_thruster.set_throttle_ew(0)
            return
        throttle_p=1
        desired_thrust=throttle_p*delta_v
        throttle_ew=-desired_thrust.dot(ew_dir)
        throttle_ns=desired_thrust.dot(ns_dir)
        self.maneuver_thruster.set_throttle_ns(throttle_ns)
        self.maneuver_thruster.set_throttle_ew(throttle_ew)
        if throttle_ns>0:
            self.thruster.set_throttle(throttle_ns)
        else:
            self.thruster.set_throttle(0)
        
        ...

    def update_navigation(self):
        #pointing control
        if self.pointing_navigation_mode==PointingNavigationMode.MANUAL:
            ...
        elif self.pointing_navigation_mode==PointingNavigationMode.SET_DIRECTION:
            self.navigation_set_direction()             
        elif self.pointing_navigation_mode==PointingNavigationMode.ZERO_ANGULAR_VELOCITY:
            self.navigation_zero_angluar_velocity()
        #velocity control
        if self.velocity_navigation_mode==VelocityNavigationMode.MANUAL:
            ...
        elif self.velocity_navigation_mode==VelocityNavigationMode.SET_VELOCITY:
            self.navigation_set_velocity()
        elif self.velocity_navigation_mode==VelocityNavigationMode.SET_THRUST:
            ew_dir=Vec2d(1,0).rotated(self.body.angle)
            ns_dir=Vec2d(0,1).rotated(self.body.angle)
            ns=ns_dir.dot(self.desired_thrust)
            ew=ew_dir.dot(self.desired_thrust)
            if ns>0:
                self.thruster.set_throttle(ns)
                self.maneuver_thruster.set_throttle_ns(0)
            else:
                self.maneuver_thruster.set_throttle_ns(ns)
                self.thruster.set_throttle(0)
            self.maneuver_thruster.set_throttle_ew(-ew)
            
        """
        if self.navigation_mode==NavigationMode.MANUAL:
            ...
        elif self.navigation_mode==NavigationMode.SET_VELOCITY:
            self.navigation_set_velocity()
        elif self.navigation_mode==NavigationMode.SET_DIRECTION:
            self.navigation_set_direction()
        elif self.navigation_mode==NavigationMode.SET_VELOCITY_AND_DIRECTION:
            self.navigation_set_direction() 
            self.navigation_set_velocity()
        elif self.navigation_mode==NavigationMode.ZERO_ANGULAR_VELOCITY:
            self.navigation_zero_angluar_velocity()
        """
            

    def thrusters_off(self):
        self.thruster.set_throttle(0)
        self.maneuver_thruster.set_throttle_ns(0)
        self.maneuver_thruster.set_throttle_ew(0)
        self.reaction_wheel.set_throttle(0)

    #call this when the ship is destroyed.
    #TODO more information about strength of explosion or how it's gonna go
    def explode(self,engine):
        self.remove_flag=True
        explosion_velocity=100
        explosion_velocity_stdev=20
        angle_stdev=0.1
        #TODO it would be best to add all the objects one frame, and then blow them apart
        #what if I added the regular magnetiles, and then a bomb object that would blow them apart?
        
        #this is a magnetile ship so disassosiate the magnetiles
        for magnetile in self.magnetiles:
            mt=magnetile.my_copy()
            mt.body.position=self.body.position+mt.body.position.rotated(self.body.angle)
            mt.body.velocity=self.body.velocity+mt.body.velocity.rotated(self.body.angle)
            mt.body.angle+=self.body.angle
            vel=random.gauss(explosion_velocity,explosion_velocity_stdev)
            angle=random.gauss(0,angle_stdev)
            mt.body.velocity+=(magnetile.body.position.normalized()*vel).rotated(angle)

            engine.schedule_add_object(mt)
        engine.add_decorator(ExplosionDecorator(position=self.body.position,velocity=self.body.velocity))  
        get_sound_store().play_sound("explosion")

    def get_sprite(self):
        ship_sprite=MagnetileConstruction.get_sprite(self)
        healthbar=HealthBar(self)
        return CompoundSprite([ship_sprite,healthbar])          

            
        

        

class Ship(GameObject):
    def __init__(self,position=Vec2d(0,0)):            
        GameObject.__init__(self)
        scale=0.5
        mass=100
        #points=[(-scale,-scale),(0,scale),(scale,-scale)]
        #mass = magnetile_density * scale * scale 
        #moment = pymunk.moment_for_poly(mass, points, (0, 0))
        #self.body = pymunk.Body(mass, moment)
        #self.shape = pymunk.Poly(self.body, points)
        self.image=get_sprite_store().get_sprite("ship1",scale=scale)
        #radius=sprite_to_sphere(self.image)
        #moment=pymunk.moment_for_circle(mass,0,radius,(0,0))        
        #self.body = pymunk.Body(mass, moment)
        #self.shape = pymunk.Circle(self.body, radius,(0,0))
        #self.body.position=position
        body,shape=get_geometry_store().get_geometry("ship1",mass,scale=scale)
        self.body=body
        self.shape=shape
        self.body.position=position
        #sprite_copy=ImageSprite(self.image,self.body.position,self.body.angle)
        #image=pygame.Surface((sprite_copy.image.get_width(),sprite_copy.image.get_height()),pygame.SRCALPHA)
        #image.fill((0,0,0,0))
        #image.blit(sprite_copy.image,(0,0))
        #self.sprite=ImageSprite(image,self.body.position,self.body.angle)
        self.sprite=ImageSprite(self.image,self.body.position,self.body.angle)
        self.geo_sprite=CircleSprite(self.shape.radius,(255,255,255),self.body.position)     
        self.length_scale=self.shape.radius   
        #parts
        self.ship_parts=[]
        self.thruster=Thruster(attachment=Vec2d(0,-self.length_scale),max_force=1e4)
        self.ship_parts.append(self.thruster)
        self.reaction_wheel=ReactionWheel(max_torque=2e5)
        self.ship_parts.append(self.reaction_wheel)
        self.maneuver_thruster=ManeuverThruster(attachment=(self.length_scale,self.length_scale),max_force=2e3,thrust_color=(128,128,128),thrust_particle_size=5)
        self.ship_parts.append(self.maneuver_thruster)
        #self.cannon=Cannon(attachment=Vec2d(0,self.length_scale))
        #self.ship_parts.append(self.cannon)
        self.cannon=LaserCannon(attachment=Vec2d(0,self.length_scale))
        self.ship_parts.append(self.cannon)
        #navigation
        self.navigation_mode=NavigationMode.MANUAL
        self.desired_direciton=Vec2d(0,1)
        self.desired_velocity=Vec2d(0,0)
        self.inertial_dampening=2e-3

    def update(self,ticks,engine):
        self.update_navigation()
        self.body.velocity=self.body.velocity*(1-self.inertial_dampening)
        GameObject.update(self,ticks,engine)
        for part in self.ship_parts:
            part.update(ticks,engine,self)        

    def get_sprite(self):
        self.sprite.set_world_position(self.body.position)
        self.sprite.set_angle(self.body.angle)
        #return self.sprite
        #self.geo_sprite.set_world_position(self.body.position)
        #self.geo_sprite.set_angle(self.body.angle)
        #return CompoundSprite([self.sprite,self.geo_sprite])        
        healthbar=HealthBar(self)
        return CompoundSprite([self.sprite,healthbar])        
        
    
    def set_desired_velocity(self,velocity):
        self.desired_velocity=velocity

    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direciton.x,self.desired_direciton.y)    
        delta_angle=desired_angle-self.body.angle
        while delta_angle>math.pi:
            delta_angle-=2*math.pi
        while delta_angle<-math.pi:
            delta_angle+=2*math.pi

        def sign(x):
            if x>0:
                return 1
            return -1
        dead_angle=0.2     
        x=delta_angle
        v=self.body.angular_velocity
        a=self.reaction_wheel.get_expected_angular_acceleration(self)        
        dt=1/60
        
        if abs(2*a*x)<=v*v and sign(x)*sign(v)>0: #if we can't stop in time
            throttle=-1*sign(x)
        else:
            throttle=1*sign(x)
        
        self.reaction_wheel.set_throttle(throttle)

    def navigation_zero_angluar_velocity(self):
        #print("zeroing angular velocity")
        self.reaction_wheel.set_throttle(-10*self.body.angular_velocity)
        

    """
    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direciton.x,self.desired_direciton.y)    
        delta_angle=desired_angle-self.body.angle
        while delta_angle>math.pi:
            delta_angle-=2*math.pi
        while delta_angle<-math.pi:
            delta_angle+=2*math.pi
        pid_p=100
        pid_v=50
        dead_angle=0.1
        if abs(delta_angle)>dead_angle:
            throttle=delta_angle*pid_p-self.body.angular_velocity*pid_v
            self.reaction_wheel.set_throttle(throttle)
        else:
            throttle=-self.body.angular_velocity*pid_v
            self.reaction_wheel.set_throttle(throttle) """

    def navigation_set_velocity(self):
        dead_velocity=0.1
        ew_dir=Vec2d(1,0).rotated(self.body.angle)
        ns_dir=Vec2d(0,1).rotated(self.body.angle)
        delta_v=self.desired_velocity-self.body.velocity
        if delta_v.length<dead_velocity:
            self.maneuver_thruster.set_throttle_ns(0)
            self.maneuver_thruster.set_throttle_ew(0)
            return
        throttle_p=1
        desired_thrust=throttle_p*delta_v
        throttle_ew=-desired_thrust.dot(ew_dir)
        throttle_ns=desired_thrust.dot(ns_dir)
        self.maneuver_thruster.set_throttle_ns(throttle_ns)
        self.maneuver_thruster.set_throttle_ew(throttle_ew)
        if throttle_ns>0:
            self.thruster.set_throttle(throttle_ns)
        else:
            self.thruster.set_throttle(0)
        
        ...

    def update_navigation(self):
        if self.navigation_mode==NavigationMode.MANUAL:
            ...
        elif self.navigation_mode==NavigationMode.SET_VELOCITY:
            self.navigation_set_velocity()
        elif self.navigation_mode==NavigationMode.SET_DIRECTION:
            self.navigation_set_direction()
        elif self.navigation_mode==NavigationMode.SET_VELOCITY_AND_DIRECTION:
            self.navigation_set_direction() 
            self.navigation_set_velocity()
        elif self.navigation_mode==NavigationMode.ZERO_ANGULAR_VELOCITY:
            self.navigation_zero_angluar_velocity()
            

    def thrusters_off(self):
        self.thruster.set_throttle(0)
        self.maneuver_thruster.set_throttle_ns(0)
        self.maneuver_thruster.set_throttle_ew(0)
        self.reaction_wheel.set_throttle(0)

