import pymunk
from pymunk import Vec2d

from sprites.Sprite import *
import math
import random
from sprites.Sprite_To_Geometry import *


magnetile_scale=40
magnetile_density=0.05

def random_magnetile_color():
    return pygame.Color(random.choice(["blue2","firebrick","goldenrod1","darkolivegreen4"]))



class GameObject:
    def __init__(self,body=None,shape=None):
        self.body=body
        self.shape=shape       

    def set_position(self,position:Vec2d):
        self.body.position=position

    def set_velocity(self,velocity:Vec2d):
        self.body.velocity=velocity 

    def get_sprite(self):
        return None
    
    def update(self,ticks,engine):
        pass
    
    def should_remove(self):
        return False
    

class ChargedSphere(GameObject):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0),radius=20,charge=1):            
        GameObject.__init__(self)
        self.charge=charge
        mass=1
        moment=pymunk.moment_for_circle(mass,0,radius,(0,0))
        self.body = pymunk.Body(mass, moment)        
        self.shape = pymunk.Circle(self.body, radius,(0,0))
        self.shape.elasticity=0.9        
        self.body.position=position
        self.body.velocity=velocity
        if charge>0:
            self.color=(255,0,0)
        else:
            self.color=(0,0,255)
        self.sprite=CircleSprite(self.shape.radius,self.color,self.body.position)
        
    def get_sprite(self):
        self.sprite.set_world_position(self.body.position)
        return self.sprite
   


class SquareMagnetile(GameObject):
    def __init__(self,position=Vec2d(0,0)):
        points=[(-magnetile_scale/2,-magnetile_scale/2),(-magnetile_scale/2,magnetile_scale/2),(magnetile_scale/2,magnetile_scale/2),(magnetile_scale/2,-magnetile_scale/2)]
        mass = magnetile_density * magnetile_scale * magnetile_scale
        moment = pymunk.moment_for_poly(mass, points, (0, 0))
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.shape = pymunk.Poly(self.body, points)
        self.shape.friction=0.5
        self.shape.elasticity=0.8        
        self.color=random_magnetile_color()


    def get_sprite(self):
        return DebugPolySprite(self.shape.get_vertices(),self.color,self.body.position,self.body.angle)
    
class RightTriangleMagnetile():
    def __init__(self,position=Vec2d(0,0)):
        points=[(-magnetile_scale/2,-magnetile_scale/2),(-magnetile_scale/2,magnetile_scale/2),(magnetile_scale/2,-magnetile_scale/2)]
        mass = magnetile_density * magnetile_scale * magnetile_scale
        moment = pymunk.moment_for_poly(mass, points, (0, 0))
        self.body = pymunk.Body(mass, moment)
        self.body.position = position
        self.shape = pymunk.Poly(self.body, points)
        self.shape.friction=0.5
        self.color=random_magnetile_color()

    def get_sprite(self):
        return DebugPolySprite(self.shape.get_vertices(),self.color,self.body.position,self.body.angle)
    
            
class Bullet(GameObject):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0),radius=5,color=(255,255,255)):            
        GameObject.__init__(self)
        mass=1
        self.color=color
        moment=pymunk.moment_for_circle(mass,0,radius,(0,0))
        self.body = pymunk.Body(mass, moment)        
        self.shape = pymunk.Circle(self.body, radius,(0,0))
        self.shape.elasticity=0.9
        print("elasticity is",self.shape.elasticity)
        self.body.position=position
        self.body.velocity=velocity
        self.sprite=CircleSprite(self.shape.radius,(0,255,0),self.body.position)
        self.lifetime=0
        self.max_lifetime=10
       
    def get_sprite(self):
        self.sprite.set_world_position(self.body.position)
        return self.sprite
    
    def update(self,ticks,engine):
        self.lifetime+=ticks/1000

    def should_remove(self):
        return self.lifetime>self.max_lifetime
        

#this is something that is drawn like a game object but has no presence in the physics
class Decorator:
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0)):
        self.position=position
        self.velocity=velocity
        self.lifetime=0
        self.max_lifetime=1

    def set_position(self,position):
        self.position=position

    def set_velocity(self,velocity):
        self.velocity=velocity

    def update(self,ticks):
        self.position+=self.velocity*ticks/1000
        self.lifetime+=ticks/1000        
        
    def should_remove(self):
        return self.lifetime>self.max_lifetime
    
    def get_sprite(self):
        return None
    
class ThrustDecorator(Decorator):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0),max_radius=10,lifetime=0.5,color=(255,0,0)):        
        Decorator.__init__(self,position,velocity)
        self.max_radius=max_radius
        self.sprite=CircleSprite(self.max_radius,color,self.position)
        self.max_lifetime=lifetime
        
    def update(self,ticks):
        Decorator.update(self,ticks)
        self.sprite.set_radius(self.max_radius*(1-self.lifetime/self.max_lifetime))        

    def get_sprite(self):
        self.sprite.set_world_position(self.position)
        return self.sprite