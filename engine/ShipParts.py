from pymunk import Vec2d
from sprites.Sprite import *
from sprites.PartSprites import *
from engine.GameObjects import *
from engine.Sound import *
from behavior_tree.ComplexBehaviors import *
from behavior_tree.TurretBehavior import *

class ShipPart:
    def __init__(self,attachement=Vec2d(0,0),ship=None):        
        self.attachment=attachement
        self.ship=ship

    def get_attachment(self):
        return self.attachment
    
    def update(self,ticks,engine,ship):
        pass

    def get_sprite(self,ship):
        return None

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

    def set_max_force(self,max_force):
        self.max_force=max_force

    def set_throttle(self,throttle): #throttle is a float from 0 to 1
        self.throttle=throttle
        if self.throttle>1:
            self.throttle=1
        if self.throttle<0:
            self.throttle=0
        #print("throttle set to ",self.throttle)

    def get_max_acceleration(self,ship):
        return self.max_force/ship.get_mass()


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
                #print("sound unpau sed throttle {}".format(self.throttle))
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

    def set_max_force(self,max_force):
        self.thruster_1.set_max_force(max_force)
        self.thruster_2.set_max_force(max_force)
        self.thruster_3.set_max_force(max_force)
        self.thruster_4.set_max_force(max_force)

    def get_max_acceleration(self,ship):
        return max(self.thruster_1.get_max_acceleration(ship),self.thruster_2.get_max_acceleration(ship),self.thruster_3.get_max_acceleration(ship),self.thruster_4.get_max_acceleration(ship))

    


class Cannon(ShipPart):
    def __init__(self,attachment=Vec2d(0,0),cooldown=0.2,projectile_speed=1300,direction=Vec2d(0,1)):
        self.attachment=attachment
        self.cooldown=cooldown
        self.burst_size=3
        self.burst_cooldown=1
        self.time_since_last_shot=0
        self.burst_count=0
        self.projectile_speed=projectile_speed
        #self.projectile_color=projectile_color
        self.firing=False
        self.direction=direction

    def fire(self):
        self.firing=True

    def update(self,ticks,engine,ship):
        self.time_since_last_shot+=ticks/1000
        if self.time_since_last_shot>self.burst_cooldown:
            self.burst_count=0
        if self.firing and self.time_since_last_shot>self.cooldown and self.burst_count<self.burst_size:
            get_sound_store().play_sound("laser")
            self.time_since_last_shot=0            
            projectile=Bullet()
            projectile.set_position(ship.body.position+self.attachment.rotated(ship.body.angle))
            projectile.set_angle(ship.body.angle)
            projectile.set_velocity(ship.body.velocity+self.direction.rotated(ship.body.angle)*self.projectile_speed)            
            engine.schedule_add_object(projectile)           
            self.burst_count+=1             
            projectile_momentum=projectile.get_mass()*projectile.body.velocity
            ship.body.apply_impulse_at_local_point(-projectile_momentum,self.attachment)
            #make_space_explosion(engine,object.position,particle_count=100,particle_lifetime=1,mean_particle_speed=100,particle_speed_sigma=10,particle_radius=2,particle_color=(255,255,255),explosion_velocity=object.velocity+self.direction.rotated_by(object.rotation)*self.projectile_speed)
            #TODO add sound effect here
            self.firing=False

    

class TorpedoLauncher(ShipPart):
    def __init__(self,attachment=Vec2d(0,0),cooldown=1,launch_velocity=200,direction=Vec2d(0,1),ammunition_instance=None):
        self.attachment=attachment
        self.cooldown=cooldown
        self.time_since_last_shot=0
        self.firing=False
        self.direction=direction
        self.launch_velocity=launch_velocity
        self.ammunition_instance=ammunition_instance
        self.ammo_count=2

    def fire(self):
        self.firing=True

    def update(self, ticks, engine, ship):
        self.time_since_last_shot+=ticks/1000
        if self.firing==True and self.time_since_last_shot>self.cooldown and self.ammo_count>0:
            self.time_since_last_shot=0
            torpedo=self.ammunition_instance()
            torpedo.set_position(ship.body.position+self.attachment.rotated(ship.body.angle))
            torpedo.set_angle(ship.body.angle)
            torpedo.set_velocity(ship.body.velocity+self.direction.rotated(ship.body.angle)*self.launch_velocity)
            torpedo.desired_direction=Vec2d(0,1).rotated(ship.body.angle)
            torpedo.behavior_tree=TorpedoBehavior(torpedo,engine)
            engine.schedule_add_object(torpedo)
            self.ammo_count-=1
            self.firing=False

class LaserCannon(ShipPart):
    def __init__(self,attachment=Vec2d(0,0),cooldown=0.2,projectile_speed=1600,direction=Vec2d(0,1)):
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

class TractorBeam(ShipPart):
    def __init__(self,attachment=Vec2d(0,0)):
        self.attachment=attachment
        self.max_distance=100
        self.force_strength=10000

    def update(self,ticks,engine,ship):
        objects=engine.point_query(ship.body.position,2*self.max_distance)
        for object in objects:            
            if isinstance(object,Collectable):                
                F=min(1,self.max_distance/(ship.body.position-object.body.position).length)
                object.body.apply_force_at_world_point(self.force_strength*(ship.body.position-object.body.position).normalized(),object.body.position)
                ship.body.apply_force_at_world_point(-self.force_strength*(ship.body.position-object.body.position).normalized(),ship.body.position)
                engine.add_decorator(TractorBeamDecorator(source=ship,target=object))

class Turret(ShipPart):
    def __init__(self,ship,attachment=Vec2d(0,0),attachment_angle=0):
        super().__init__(attachment,ship)
        #self.max_angle=-math.pi*3/4
        self.max_angle=math.pi/4
        self.min_angle=-math.pi/4
        self.attachment_angle=attachment_angle
        self.angle=self.attachment_angle
        #TODO handle straight down
        self.weapon=Cannon(attachment=Vec2d(0,0),cooldown=0.2,projectile_speed=1600,direction=Vec2d(0,1))   
        self.behavior=None

    def get_position(self):
        return self.ship.body.position+self.attachment.rotated(self.ship.body.angle)
    
    def get_world_angle(self):
        return self.ship.body.angle+self.attachment_angle+self.angle

    def get_world_mount_angle(self):
        return self.ship.body.angle+self.attachment_angle
    
    def angle_to_world_angle(self,angle):
        return angle-self.ship.body.angle-self.attachment_angle
    
    def set_angle_to_world_angle(self,angle):
        target_angle=self.angle_to_world_angle(angle)
        if target_angle>math.pi:
            target_angle-=2*math.pi        
        if target_angle<0:
            if target_angle<self.min_angle:
                target_angle=self.min_angle
        else:
            if target_angle>self.max_angle:
                target_angle=self.max_angle
        
        #print("target angle ",target_angle)
        self.angle=target_angle
        

    def update(self,ticks,engine,ship):
        if self.behavior==None:
            #self.behavior=TurretBehaviorScan(self,None)     
            self.behavior=DefaultTurretBehavior(self,engine,{})
        self.behavior.execute()
        #self.angle+=ticks*0.001        
        #self.fire_weapon(ship)
        if self.weapon!=None:
            self.weapon.update(ticks,engine,ship)
        pass  
    
    def get_sprite(self,ship):        
        #ret=CircleSprite(20,(100,100,100))        
        ret=TurretSprite(self)
        ret.set_world_position(ship.body.position+self.attachment.rotated(ship.body.angle))
        ret.ship_angle=ship.body.angle
        return ret
    
    def fire_weapon(self):
        if self.weapon!=None:
            #the weapon itself takes care of ship angle
            self.weapon.direction=Vec2d(0,1).rotated(self.attachment_angle+self.angle)
            self.weapon.attachment=self.attachment
            self.weapon.fire()
            #print("yep I'm firing") #TODO why is this sideways??