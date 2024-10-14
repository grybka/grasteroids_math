from engine.GameObjects import *
from pymunk import Vec2d
from sprites.Sprite import *    
from sprites.SpriteSheet import get_sprite_store
from engine.ShipParts import *
from engine.Enums import *
from engine.Magnetile import *
from behavior_tree.BehaviorTree import BTreeResponse
import random



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
        self.is_trackable=True

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
    
    def get_max_angular_velocity(self):
        return 0
    
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
        #self.thruster=Thruster(attachment=Vec2d(0,self.radius),max_force=mass*100)
        self.thruster=Thruster(attachment=Vec2d(0,self.radius),max_force=mass*500)
        self.ship_parts.append(self.thruster)
        self.reaction_wheel=ReactionWheel(max_torque=moment*8)
        self.ship_parts.append(self.reaction_wheel)
        self.reactor_breach=False
        self.lifetime=0
        self.max_lifetime=20
        self.image=get_sprite_store().get_sprite("missile",scale=2)
        self.sprite=ImageSprite(self.image,self.body.position,self.body.angle)

    def get_max_angular_velocity(self):
        return self.reaction_wheel.max_angular_velocity
    
    def get_shields(self):
        return 0,0



    def get_sprite(self):
        #ns_dir=Vec2d(0,1).rotated(self.body.angle)        
        #return CompoundSprite([CircleSprite(10,(0,255,255),world_position=self.body.position+10*ns_dir),CircleSprite(10,(255,0,255),world_position=self.body.position-10*ns_dir)])
        self.sprite.set_world_position(self.body.position)
        self.sprite.set_angle(self.body.angle)
        return self.sprite

    def do_damage(self,damage):
        self.reactor_breach=True

    def update_navigation(self):
        self.navigation_set_direction()
        self.navigation_set_velocity()


# I want to minimize chi=(v-desired_velocity)^2
# dchi= 2*(v-desired_velocity) dot dv - 2*(v-desired_velocity) dot dv_desired

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
        self.lifetime+=ticks/1000
        self.update_navigation()
        for part in self.ship_parts:
            part.update(ticks,engine,self)  
        if self.reactor_breach or self.lifetime>self.max_lifetime:
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
            max_force=5e4
            dx=obj.body.position-self.body.position
            obj.body.apply_impulse_at_world_point( max_force*dx/(dx.length+1),obj.body.position)
        get_sound_store().play_sound("explosion2")

        self.remove_flag=True
        ...



