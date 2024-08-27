from engine.GameObjects import *
from pymunk import Vec2d
from sprites.Sprite import *    
from sprites.SpriteSheet import get_sprite_store
from engine.ShipParts import *
from enum import Enum

class NavigationMode(enum):
    MANUAL=1
    SET_DIRECTION=2
    SET_VELOCITY=3
    SET_VELOCITY_AND_DIRECTION=4
    SET_POSITION=5

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
        #navigation
        self.navigation_mode=NavigationMode.MANUAL
        self.desired_direciton=Vec2d(0,1)
        self.desired_velocity=Vec2d(0,0)

    def update(self,ticks,engine):
        self.update_navigation()
        GameObject.update(self,ticks,engine)
        for part in self.ship_parts:
            part.update(ticks,engine,self)        

    def get_sprite(self):
        self.sprite.set_world_position(self.body.position)
        self.sprite.set_angle(self.body.angle)
        self.geo_sprite.set_world_position(self.body.position)
        self.geo_sprite.set_angle(self.body.angle)
        #return CompoundSprite([self.sprite,self.geo_sprite])        
        return self.sprite
    
    def fire_cannon(self,engine):
        pos=self.body.position+Vec2d(0,self.length_scale).rotated(self.body.angle)
        bullet=Bullet(pos,self.body.velocity+Vec2d(0,500).rotated(self.body.angle))
        #bullet.body.apply_impulse_at_local_point(Vec2d(0,1e5),(0,0))
        print("firing bullet")
        engine.add_object(bullet)

    def set_desired_velocity(self,velocity):
        self.desired_velocity=velocity

    def navigation_set_direction(self):
        desired_angle=math.atan2(-self.desired_direciton.x,self.desired_direciton.y)    
        delta_angle=desired_angle-self.body.angle
        pid_p=100
        pid_v=50
        dead_angle=0.1
        if abs(delta_angle)>dead_angle:
            throttle=delta_angle*pid_p-self.body.angular_velocity*pid_v
            self.reaction_wheel.set_throttle(throttle)
        else:
            throttle=-self.body.angular_velocity*pid_v
            self.reaction_wheel.set_throttle(throttle) 

    def navigation_set_velocity(self):
        ew_dir=Vec2D(1,0).rotated(self.body.angle)
        ns_dir=Vec2D(0,1).rotated(self.body.angle)
        delta_v=self.desired_velocity-self.body.velocity
        throttle_p=100
        desired_thrust=throttle_p*delta_v
        throttle_ew=desired_thrust.dot(ew_dir)
        throttle_ns=desired_thrust.dot(ns_dir)
        self.maneuver_thruster.set_throttle_ns(throttle_ns)
        self.maneuver_thruster.set_throttle_ew(throttle_ew)
        #TODO main thruster
        
        ...

    def update_navigation(self):
        if self.navigation_mode==NavigationMode.MANUAL:
            ...
        elif self.navigation_mode==NavigationMode.SET_VELOCITY:
            ...
        elif self.navigation_mode==NavigationMode.SET_DIRECTION:
            self.navigation_set_direction()
        elif self.navigation_mode==NavigationMode.SET_VELOCITY_AND_DIRECTION:
            self.navigation_set_direction() 
