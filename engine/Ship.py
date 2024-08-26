from engine.GameObjects import *
from pymunk import Vec2d
from sprites.Sprite import *    
from sprites.SpriteSheet import get_sprite_store


class ShipPart:
    def __init__(self,attachement=Vec2d(0,0)):
        self.attachment=attachement

    def get_attachment(self):
        return self.attachment
    
    def update(self,ticks,engine,ship):
        pass

class Thruster(ShipPart):
    def __init__(self,**kwargs):
        defaultKwargs={"max_force":100,"attachment":Vec2d(0,0),"direction":Vec2d(0,1),"thrust_color":(255,255,0),"thrust_particle_size_per_force":0.1,"thrust_particle_speed":100,"thrust_particle_period":0.1}
        kwargs = { **defaultKwargs, **kwargs }
        ShipPart.__init__(self,kwargs["attachment"])
        self.throttle=0
        self.max_force=kwargs["max_force"]
        self.direction=kwargs["direction"] #direction that the thruster points in
        #regarding thrust particles
        self.time_since_last_thrust_particle=0
        self.thrust_particle_period=kwargs["thrust_particle_period"]
        self.thrust_particle_speed=kwargs["thrust_particle_speed"]
        self.thrust_particle_size_per_force=kwargs["thrust_particle_size_per_force"]
        self.thrust_color=kwargs["thrust_color"]

    def set_throttle(self,throttle): #throttle is a float from 0 to 1
        self.throttle=throttle
        if self.throttle>1:
            self.throttle=1
        if self.throttle<0:
            self.throttle=0
        print("throttle set to ",self.throttle)


    def update(self,ticks,engine,ship):
        if self.throttle>0:
            total_force=self.throttle*self.max_force*self.direction
            ship.body.apply_force_at_local_point(total_force,self.attachment)
            #thrust particles
            if self.time_since_last_thrust_particle>self.thrust_particle_period:        
                self.time_since_last_thrust_particle=0
                particle=ThrustDecorator()
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
        ShipPart.__init__(self,Vector2D(0,0))        
        self.thruster_1=Thruster(attachment=Vec2d(0,attachment[1]),direction=Vec2d(0,1),**kwargs)        
        self.thruster_2=Thruster(attachment=Vec2d(0,-attachment[1]),direction=Vec2d(0,-1),**kwargs)        
        self.thruster_3=Thruster(attachment=Vec2d(attachment[0],0),direction=Vec2d(1,0),**kwargs)        
        self.thruster_4=Thruster(attachment=Vec2d(-attachment[0],0),direction=Vec2d(-1,0),**kwargs)

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
        self.reaction_wheel=ReactionWheel(max_torque=2e4)
        self.ship_parts.append(self.reaction_wheel)
        self.maneuver_thruster=ManeuverThruster(attachment=(self.length_scale,self.length_scale),max_force=2e3)
        self.ship_parts.append(self.maneuver_thruster)

    def update(self,ticks,engine):
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
