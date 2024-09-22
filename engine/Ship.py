from engine.GameObjects import *
from pymunk import Vec2d
from sprites.Sprite import *    
from sprites.SpriteSheet import get_sprite_store
from engine.ShipParts import *
from enum import Enum
from engine.Magnetile import *
from engine.BehaviorTree import BTreeResponse
import random

class PointingNavigationMode(Enum):
    MANUAL=1
    SET_DIRECTION=2
    ZERO_ANGULAR_VELOCITY=3

class VelocityNavigationMode(Enum):
    MANUAL=1
    SET_VELOCITY=2
    SET_THRUST=3


class ControllableShip(GameObject):
    def __init__(self):
        ...
        self.pointing_navigation_mode=PointingNavigationMode.MANUAL
        self.velocity_navigation_mode=VelocityNavigationMode.MANUAL
        self.desired_acceleration=Vec2d(0,0)
        self.desired_velocity=Vec2d(0,0)
        self.desired_direction=Vec2d(0,1)
        self.firing=False
        self.is_dead=False
        self.behavior_tree=None

    def set_pointing_navigation_mode(self,mode):
        self.pointing_navigation_mode=mode

    def set_velocity_navigation_mode(self,mode):
        self.velocity_navigation_mode=mode
    
    def set_desired_velocity(self,velocity):
        self.desired_velocity=velocity

    def set_desired_direction(self,direction):
        self.desired_direction=direction

    def set_desired_acceleration(self,acceleration):
        self.desired_acceleration=acceleration
    
    def get_max_acceleration(self,direction):
        return Vec2d(0,0)
    
    def set_firing(self,firing):
        self.firing=firing

    def update(self,ticks,engine):
        super().update(ticks,engine)
        #behavior
        if self.behavior_tree:
            if self.behavior_tree.execute()==BTreeResponse.SUCCESS:
                self.behavior_tree=None
#            self.behavior_tree.execute()



        #space resistance
        #F = - lambda * mass * v^2 v
        L=1e-6
        vsquared=self.body.velocity.get_length_sqrd()
        #for stability
        if vsquared>1e6:
            vsquared=1e6
        force=-L*vsquared*self.body.velocity*self.get_mass()       
        self.body.apply_force_at_world_point(force,self.body.position)

class Torpedo(ControllableShip):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0)):
        ControllableShip.__init__(self)
        self.radius=5

        

        mass=1        
        moment=pymunk.moment_for_circle(mass,0,self.radius,(0,0))
        self.body = pymunk.Body(mass, moment)   
        self.body.position=position     
        self.body.velocity=velocity
        self.shape = pymunk.Circle(self.body, self.radius,(0,0))
        self.shape.collision_type=COLLISION_TYPE_SHIP
        self.shape.elasticity=0.9
        self.remove_flag=False
        self.ship_parts=[]
        self.thruster=Thruster(attachment=Vec2d(0,self.radius),max_force=mass*100)
        self.ship_parts.append(self.thruster)
        self.reaction_wheel=ReactionWheel(max_torque=moment*8)
        self.ship_parts.append(self.reaction_wheel)
        self.reactor_breach=False


    def get_sprite(self):
        ns_dir=Vec2d(0,1).rotated(self.body.angle)

        
        return CompoundSprite([CircleSprite(10,(0,255,255),world_position=self.body.position+10*ns_dir),CircleSprite(10,(255,0,255),world_position=self.body.position-10*ns_dir)])

    def do_damage(self,damage):
        self.reactor_breach=True

    def update_navigation(self):
        self.navigation_set_direction()
        self.navigation_set_velocity()

    def navigation_set_velocity(self):
        dead_velocity=0.1
        ns_dir=Vec2d(0,1).rotated(self.body.angle)
        delta_v=self.desired_velocity-self.body.velocity
        delta_v1d=delta_v.dot(ns_dir)
        if delta_v1d<dead_velocity:
            self.thruster.set_throttle(0)
            return
        if delta_v1d>0:
            self.thruster.set_throttle(1)
        else:
            self.thruster.set_throttle(0)

    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direction.x,self.desired_direction.y)    
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

    def update(self,ticks,engine):
        super().update(ticks,engine)
        self.update_navigation()
        for part in self.ship_parts:
            part.update(ticks,engine,self)  
        if self.reactor_breach:
            self.explode(engine)

    def explode(self,engine):
        #make the explosion animation
        engine.add_decorator(ExplosionDecorator(position=self.body.position,velocity=self.body.velocity,animation_name="explosion2"))  
        #damage nearby objects
        explosion_radius=100
        nearby_objects=engine.point_query(self.body.position,explosion_radius)
        print("nearby object count",len(nearby_objects))
        for obj in nearby_objects:
            if isinstance(obj,ControllableShip):
                obj.do_damage(15)
        get_sound_store().play_sound("explosion2")

        self.remove_flag=True
        ...



class MagnetileShip(MagnetileConstruction, ControllableShip):
    def __init__(self,position=Vec2d(0,0),shape_fname=None):  

        MagnetileConstruction.__init__(self,shape_fname=shape_fname) 
        ControllableShip.__init__(self)                
        bbox=self.get_bbox()
        self.bbox=bbox
      
        #parts
        self.shield_recharge_rate=0.1
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
        
        
        
        self.inertial_dampening=2e-3
        

        #game stats
        self.max_health=10
        self.health=10
        self.max_shields=10
        self.shields=10
        self.reactor_breach=False    

    def update(self,ticks,engine):
        MagnetileConstruction.update(self,ticks,engine)
        #super().update(ticks,engine)
        self.update_navigation()        
        #self.body.velocity=self.body.velocity*(1-self.inertial_dampening)
        #GameObject.update(self,ticks,engine)
        ControllableShip.update(self,ticks,engine)
        for part in self.ship_parts:
            part.update(ticks,engine,self)  
        if self.reactor_breach:
            self.explode(engine)   
        if self.shields<self.max_shields:
            self.shields+=self.shield_recharge_rate*ticks/1000   

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

    def get_max_acceleration(self,direction):
        return self.maneuver_thruster.get_max_acceleration(self)        

    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direction.x,self.desired_direction.y)    
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
        if throttle_ns>0.2:
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
                frac_thottle=self.maneuver_thruster.get_max_acceleration(self)/self.thruster.get_max_acceleration(self)
                maneuver_throttle=ns/frac_thottle
                if abs(maneuver_throttle)<=1:
                    self.maneuver_thruster.set_throttle_ns(maneuver_throttle)
                    self.thruster.set_throttle(0)
                else:                    
                    self.thruster.set_throttle(ns)
                    self.maneuver_thruster.set_throttle_ns(0)
            else:
                self.maneuver_thruster.set_throttle_ns(ns)
                self.thruster.set_throttle(0)
            self.maneuver_thruster.set_throttle_ew(-ew)

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
            mt.max_lifetime=10 #make them fade away after 10 seconds
            mt.body.position=self.body.position+mt.body.position.rotated(self.body.angle)
            mt.body.velocity=self.body.velocity+mt.body.velocity.rotated(self.body.angle)
            mt.body.angle+=self.body.angle
            vel=random.gauss(explosion_velocity,explosion_velocity_stdev)
            angle=random.gauss(0,angle_stdev)
            mt.body.velocity+=(magnetile.body.position.normalized()*vel).rotated(angle)

            engine.schedule_add_object(mt)
        engine.add_decorator(ExplosionDecorator(position=self.body.position,velocity=self.body.velocity))  
        get_sound_store().play_sound("explosion")
        self.is_dead=True

    def get_sprite(self):
        ship_sprite=MagnetileConstruction.get_sprite(self)
        healthbar=HealthBar(self)
        return CompoundSprite([ship_sprite,healthbar])        

    def set_firing(self,firing):
        if firing:
            self.cannon.fire()        

class ShipFactory:
    def __init__(self):
        self.ship_info={}

    def load_ship_info(self,fname):
        with open(fname) as f:
            self.ship_info=yaml.safe_load(f)

    def get_ship(self,ship_name):
        if ship_name not in self.ship_info:
            return None
        info=self.ship_info[ship_name]
        ret=MagnetileShip(shape_fname=info["tile_arrangement"])
        ret.maneuver_thruster.set_max_force(info["maneuver_acceleration"]*ret.get_mass())
        ret.thruster.set_max_force(info["thruster_acceleration"]*ret.get_mass())
        print("rotational acceleration is",info["rotational_acceleration"])
        ret.reaction_wheel.max_torque=info["rotational_acceleration"]*ret.get_moment()
        ret.reaction_wheel.max_angular_velocity=info["max_rotational_speed"]        
        print("max torque is",ret.reaction_wheel.max_torque)
        ret.shield_recharge_rate=info["shield_recharge_rate"]
        return ret
        

_ship_factory=ShipFactory()

def get_ship_factory():
    return _ship_factory
