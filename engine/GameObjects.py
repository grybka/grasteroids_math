import pymunk
from pymunk import Vec2d

from sprites.Sprite import *
import math
import random
from sprites.Sprite_To_Geometry import *
from sprites.SpriteAnimations import get_sprite_animation_store

COLLISION_TYPE_SHIP=1
COLLISION_TYPE_BULLET=2


class GameObject:
    def __init__(self,body=None,shape=None):
        self.body=body 
        self.shape=shape #a pymunk shape or list of shapes
        self.remove_flag=False
        self.is_trackable=False

    def set_position(self,position:Vec2d):
        self.body.position=position

    def set_angle(self,angle:float):
        self.body.angle=angle

    def set_velocity(self,velocity:Vec2d):
        self.body.velocity=velocity 

    def get_sprite(self):
        return None
    
    def update(self,ticks,engine):
        pass
    
    def should_remove(self):
        return self.remove_flag
    
    def get_mass(self):
        if isinstance(self.shape,list):
            return sum([s.mass for s in self.shape])
        return self.shape.mass
    

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
   


            
class Bullet(GameObject):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0)):            
        GameObject.__init__(self)
        radius=5
        mass=1        
        moment=pymunk.moment_for_circle(mass,0,radius,(0,0))
        self.body = pymunk.Body(mass, moment)        
        self.shape = pymunk.Circle(self.body, radius,(0,0))
        self.shape.collision_type=COLLISION_TYPE_BULLET
        self.shape.elasticity=0.9
        #print("elasticity is",self.shape.elasticity)
        self.body.position=position
        self.body.velocity=velocity
        #self.sprite=CircleSprite(self.shape.radius,(0,255,0),self.body.position)
        self.image=get_sprite_store().get_sprite("bullet",scale=1)
        self.sprite=ImageSprite(self.image,self.body.position,self.body.angle)

        self.lifetime=0
        self.max_lifetime=10    
        self.hit_this_frame=False
    
    def get_sprite(self):
        self.sprite.set_world_position(self.body.position)
        #self.sprite.set_angle(self.body.angle)                
        self.sprite.set_angle(self.body.velocity.angle+math.pi/2)
        return self.sprite
    
    def update(self,ticks,engine):
        self.lifetime+=ticks/1000
        self.hit_this_frame=False


    def flag_remove(self):
        self.lifetime=self.max_lifetime+1

    def should_remove(self):
        return self.lifetime>self.max_lifetime
        
class LaserBeam(GameObject):
    def __init__(self,start_position=Vec2d(0,0),velocity=Vec2d(0,0),angle=0,length=160,radius=2,anim_name="laser_beam"):
        GameObject.__init__(self)
        self.start_position=start_position
        self.length=length
        self.body = pymunk.Body()                
        #lets make the position the 'front' of the segment        
        self.shape = pymunk.Segment(self.body, self.start_position,self.start_position,radius)
        self.shape.collision_type=COLLISION_TYPE_BULLET
        self.shape.elasticity=0.9
        self.shape.density=0.1
        #print("elasticity is",self.shape.elasticity)
        self.body.position=start_position
        self.body.velocity=velocity
        self.body.angle=angle
        frames,frame_time=get_sprite_animation_store().get_animation(anim_name)
        self.sprite=AnimationSprite(frames,self.body.position)        
        self.lifetime=0
        self.max_lifetime=10
        self.start_pos=start_position
        self.growing_mode=1
        #self.end_pos=start_position
        #there are 3 states this can be in
        #1) the beam is growing to full size
        #2) the beam is at full size
        #3) the beam is shrinking to zero size

    def update_shape(self):
        d=(self.body.position-self.start_position).length
        if d<self.length:
            self.start_pos=self.start_position
            self.end_pos=self.start_position+self.body.position
            self.shape.unsafe_set_endpoints(self.start_position,self.body.position)
        else:
            self.growing_mode=2
        #if it's long enough, it doesn't need to be updated
        #TODO what happens at the end?                
       
    def get_sprite(self):      
        if self.growing_mode==1:
            pos=0.5*(self.start_pos+self.body.position)  
        else:
            dirvec=(self.body.position-self.start_pos).normalized()
            pos=self.body.position-dirvec*self.length/2
        self.sprite.set_world_position(pos)
        self.sprite.set_angle(self.body.angle)
        self.sprite.clip_rect=(0,0,None,int((self.body.position-self.start_pos).length))   
        return self.sprite
    
    def update(self,ticks,engine):
        self.lifetime+=ticks/1000
        self.update_shape()
        self.sprite.update(ticks)

    def should_remove(self):
        return self.lifetime>self.max_lifetime
        


#this is something that is drawn like a game object but has no presence in the physics
class Decorator:
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0)):
        self.position=position
        self.velocity=velocity
        self.lifetime=0
        self.max_lifetime=1
        self.top_layer=True #draw on top of objects

    def set_position(self,position):
        self.position=position

    def set_velocity(self,velocity):
        self.velocity=velocity

    def update(self,ticks,engine=None):
        self.position+=self.velocity*ticks/1000
        self.lifetime+=ticks/1000        
        
    def should_remove(self):
        if self.max_lifetime<=0:
            return False
        return self.lifetime>self.max_lifetime
    
    def get_sprite(self):
        return None
    
#a decorator that has a standard image sprite
class SpriteDecorator(Decorator):
    def __init__(self,position=Vec2d(0,0),image_name="planet1"):        
        super().__init__(position)
        self.image_name=image_name
        self.image=get_sprite_store().get_sprite(image_name)
        self.sprite=ImageSprite(self.image,self.position)
        self.max_lifetime=-1
        self.top_layer=False

    def get_sprite(self):
        return self.sprite

class ThrustDecorator(Decorator):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0),max_radius=10,lifetime=0.5,color=(255,0,0)):        
        Decorator.__init__(self,position,velocity)
        self.max_radius=max_radius
        self.sprite=CircleSprite(self.max_radius,color,self.position)
        self.max_lifetime=lifetime
        
    def update(self,ticks,engine=None):
        Decorator.update(self,ticks)
        self.sprite.set_radius(self.max_radius*(1-self.lifetime/self.max_lifetime))        

    def get_sprite(self):
        self.sprite.set_world_position(self.position)
        return self.sprite
    
class ExplosionDecorator(Decorator):
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0),animation_name="explosion"):
        Decorator.__init__(self,position,velocity)
        frames,frame_time=get_sprite_animation_store().get_animation(animation_name)
        self.sprite=AnimationSprite(frames,position,frame_time=frame_time)
        self.max_lifetime=len(frames)*frame_time

    def update(self,ticks,engine=None):
        Decorator.update(self,ticks)
        self.sprite.update(ticks)

    def get_sprite(self):
        self.sprite.set_world_position(self.position)
        return self.sprite
    
class ParticleSprayDecorator(Decorator):
    #tuples indicate mean,standrd deviation
    def __init__(self,position=Vec2d(0,0),velocity=Vec2d(0,0),particle_count=10,particle_lifetime=(1.0,0.1),radius=(2,1),relative_speed=(400,10),color=(100,100,100)):
        Decorator.__init__(self,position,velocity)
        self.particles=[]
        for i in range(particle_count):
            lifetime=random.gauss(*particle_lifetime)
            speed=random.gauss(*relative_speed)
            r=abs(random.gauss(*radius))
            angle=random.random()*2*math.pi
            velocity=Vec2d(math.cos(angle),math.sin(angle))*speed
            self.particles.append([lifetime,r,velocity])        
        self.color=color
        self.max_lifetime=max([p[0] for p in self.particles])        

    def update(self,ticks,engine=None):
        Decorator.update(self,ticks)                

    def get_sprite(self):
        my_position=self.position+self.lifetime*self.velocity
        sprites=[]
        for p in self.particles:
            if self.lifetime>p[0]:
                continue
            position=my_position+p[2]*self.lifetime
            sprite=CircleSprite(p[1],self.color,position)
            sprites.append(sprite)
        return CompoundSprite(sprites)

class ShipSpawnDecorator(Decorator):
    def __init__(self,position,ship):
        Decorator.__init__(self,position)
        self.ship=ship
        
    def update(self,ticks,engine):
        Decorator.update(self,ticks)
        if self.should_remove():
            engine.schedule_add_object(self.ship)

    def get_sprite(self):
        #scale=1-self.lifetime/self.max_lifetime
        scale=self.lifetime/self.max_lifetime
        image=self.ship.get_sprite().get_image()
        to_blit=pygame.transform.scale(image,(int(image.get_width()*scale),int(image.get_height()*scale)))
        return ImageSprite(to_blit,self.position)



        