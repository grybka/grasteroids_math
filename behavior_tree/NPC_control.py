
from engine.Enums import *
from pymunk import Vec2d
import math
import random 
from behavior_tree.BehaviorTree import *

def sign(x):    
    if x<0:
        return -1    
    return 1

def move_to_point(x0,x,v,amax):
    #Amax is the maximum acceleration I can use
    safety_margin=0.9 #this is the fraction of the acceleration I want to use
    dx=x0-x #direction I want to move in
    #print("mtp dx",dx)
    #I either need to accelerate in that direction, or decelrate because I will overshoot
    #Condition for overshoot a*dx=v^2/2    
    sign_dx=sign(dx)
    sign_v=sign(v)
    #print("dx sign dx sign v",dx,sign_dx,sign_v)
    if dx==0:
        return 0
    if abs(safety_margin*amax*dx)<=v**2/2 and sign_dx==sign_v:
        #decelerate
        #print("decellerate")
        desired_accel=v**2/(2*dx)
        return -sign_dx*desired_accel/amax
    else:
        #accelerate
        #print("accelerate")
        return sign_dx
    
def angle_subtract(a,b):
    x=a-b
    while x>math.pi:
        x-=2*math.pi
    while x<-math.pi:
        x+=2*math.pi
    return x




#Unaware ships
#Pick a random point in space
#Fly towards it
#if you see the player ship, chase it

#Aware ships
#I want to be pointing towards player ship
#when there's a decent chance of hitting it, fire

    
class TurnTowardsPlayer(BehaviorTree):
    def __init__(self,npc,player,angle_threshold=0.1):
        self.npc=npc
        self.player=player
        self.angle_threshold=angle_threshold

    def execute(self):
        return TurnTowardsPoint(self.npc,self.player.body.position,self.angle_threshold)
        
class TurnTowardsPoint(BehaviorTree):
    def __init__(self,npc, point,angle_threshold=0.1):
        self.npc=npc
        self.point=point
        self.angle_threshold=angle_threshold

    def execute(self):
        desired_direction=self.point-self.npc.body.position
        current_angle=self.npc.body.angle+math.pi/2
        if abs(desired_direction.angle-current_angle)<self.angle_threshold:
            return BTreeResponse.SUCCESS
        self.npc.set_desired_direction(desired_direction.normalized())
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        
        return BTreeResponse.RUNNING


class MoveToPoint(BehaviorTree):
    def __init__(self,npc ,point,point_threshold=5):
        self.npc=npc
        self.point=point
        self.point_threshold=point_threshold

    def execute(self):        
        dx=self.point-self.npc.body.position        
        amax=self.npc.get_max_acceleration(-dx.normalized())
        #I want to be going at a velocity such that my stopping distance is the distance to the point
        #0.5 v^2 = a dx
        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)            
        if dx.length<self.point_threshold:            
            self.npc.set_desired_velocity(Vec2d(0,0))
            return BTreeResponse.SUCCESS
        ideal_velocity_magnitude=math.sqrt(2*amax*dx.length)
        ideal_velocity=dx.normalized()*ideal_velocity_magnitude        
        self.npc.set_desired_velocity(ideal_velocity)
        return BTreeResponse.RUNNING
    
class HoldPosition(BehaviorTree):
    def __init__(self,npc):
        self.npc=npc                

    def execute(self):   
        print("hold position")
        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)
        self.npc.desired_thrust=Vec2d(0,0)        
        return BTreeResponse.SUCCESS     

class FireAtPlayer(BehaviorTree):
    def __init__(self,npc,target_name,data,fire_threshold=0.1):
        self.npc=npc        
        self.fire_threshold=fire_threshold
        self.target_name=target_name
        self.data=data

    def execute(self):
        if self.target_name not in self.data:
            return BTreeResponse.FAILURE
        target=self.data[self.target_name]
        dx=target.body.position-self.npc.body.position
        delta_velocity=target.body.velocity-self.npc.body.velocity
        projectile_speed=self.npc.cannon.projectile_speed
        desired_direction=dx+(dx.length/projectile_speed)*delta_velocity




        delta_angle=angle_subtract(desired_direction.angle-math.pi/2,self.npc.body.angle)

        #print("delta_angle",delta_angle)
        if abs(delta_angle)<self.fire_threshold:
            self.npc.set_firing(True)
            #print("fire")
            return BTreeResponse.RUNNING

        
        self.npc.set_firing(False)
        self.npc.set_desired_direction(target.body.position-self.npc.body.position)
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        
        return BTreeResponse.RUNNING

class WanderRandomly(BehaviorTree):
    def __init__(self,npc,arena_size=(-2000,-2000,4000,4000),timescale=20*60):
        self.npc=npc
        self.arena_size=arena_size
        self.target=Vec2d(0,0)
        self.timescale=timescale
        self.time_since_last_target=timescale
        self.sub_behavior=None

    def execute(self):
        self.time_since_last_target+=1
        if self.time_since_last_target>self.timescale:          
            self.target=Vec2d(self.arena_size[0]+self.arena_size[2]*random.random(),self.arena_size[1]+self.arena_size[3]*random.random())
            print("New wander target",self.target)
            self.time_since_last_target=0
            self.sub_behavior=ParallelBehavior([DoOnce(TurnTowardsPoint(self.npc,self.target)),MoveToPoint(self.npc,self.target)])
        if self.sub_behavior is not None:
            if self.sub_behavior.execute()==BTreeResponse.SUCCESS:
                self.time_since_last_target=self.timescale
        #if MoveToPoint(self.npc,self.target).execute()==BTreeResponse.SUCCESS:
            #self.time_since_last_target=self.timescale
        return BTreeResponse.RUNNING
    
class InterceptShip(BehaviorTree):
    def __init__(self,npc,target_name,data,ideal_velocity=1000):
        super().__init__(npc,data)        
        self.target_name=target_name
        self.ideal_velocity=ideal_velocity #magnitude

    def execute(self):
        if self.target_name not in self.data:
            return BTreeResponse.FAILURE
        ship=self.data[self.target_name]

        #turn_part=TurnTowardsPlayer(self.npc,self.ship).execute()
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        

        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY) 
        dx=ship.body.position-self.npc.body.position
        current_velocity=self.npc.body.velocity
        ideal_velocity_mag=min(self.ideal_velocity,current_velocity.length+self.ideal_velocity*0.1)
        #ideal_velocity_mag=self.ideal_velocity
        target_velocity=ideal_velocity_mag*dx.normalized()+ship.body.velocity
        #if it is moving out of my field of view faster than I can turn, then just try to match velocity
        omega=dx.cross(current_velocity-ship.body.velocity)/(dx.length**2)
        #print("omega {} max angular velocity {}".format(omega,self.npc.get_max_angular_velocity()))
        if abs(omega)>self.npc.get_max_angular_velocity():
            #print("omega",omega)
            target_velocity=ship.body.velocity
            self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_THRUST)
            self.npc.desired_thrust=Vec2d(0,0)
        #if it's too far out of my field of view anyways, turn off the thrusters
        my_direction=Vec2d(0,1).rotated(self.npc.body.angle).angle
        if abs(angle_subtract(target_velocity.angle,my_direction))<math.pi/4:
            self.npc.set_desired_velocity(target_velocity)
        else:
            print("manual target velocity angle {} my direction {}".format(target_velocity.angle,my_direction))
            self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_THRUST)
            self.npc.desired_thrust=Vec2d(0,0)               
            
        
        dv=target_velocity-current_velocity
        self.npc.set_desired_direction(dv.normalized())


        return BTreeResponse.RUNNING           

class SearchForTarget(BehaviorTree):
    def __init__(self,npc,data,engine,target_name="target"):
        super().__init__(npc,data)
        self.engine=engine
        self.max_distance=10000
        self.angle_range=math.pi/4
        self.last_target=None
        self.target_name=target_name

    def execute(self):
        position=self.npc.body.position
        angle=self.npc.body.angle
        objects=self.engine.point_query(position,self.max_distance)
        objects_in_view_cone=[]
        for object in objects:
            if object==self.npc:
                continue
            dx=object.body.position-position
            angle_to_object=dx.angle-math.pi/2
            delta_angle=angle_subtract(angle_to_object,angle)
            #print("angle to {} delta angle {}".format(object,delta_angle))
            #print("self navigation mode {}".format(self.npc.pointing_navigation_mode))
            if abs(delta_angle)<self.angle_range and object!=self.npc:
                if object.is_trackable:
                    objects_in_view_cone.append(object)        
        if len(objects_in_view_cone)==0:
            self.data[self.target_name]=None
            return BTreeResponse.FAILURE            
        if self.last_target in objects_in_view_cone:
            self.data[self.target_name]=self.last_target
            return BTreeResponse.SUCCESS        
        self.last_target=objects_in_view_cone[0]        
        self.data[self.target_name]=self.last_target
        return BTreeResponse.SUCCESS
    
class ApproachToDistance(BehaviorTree):
    def __init__(self,npc,target_name,data,distance=100):
        super().__init__(npc,data)
        self.target_name=target_name
        self.distance=distance

    def execute(self):        
        if self.target_name not in self.data:
            return BTreeResponse.FAILURE
        target=self.data[self.target_name]
        dx=target.body.position-self.npc.body.position
        if dx.length<self.distance:
            return BTreeResponse.SUCCESS
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)
        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)
        max_speed=1000
        self.npc.set_desired_velocity(dx.normalized()*max_speed)
        self.npc.set_desired_direction(dx.normalized())

        return BTreeResponse.RUNNING
    
class ZeroVelocity(BehaviorTree):
    def __init__(self,npc):
        self.npc=npc

    def execute(self):
        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)
        self.npc.set_desired_velocity(Vec2d(0,0))
        return BTreeResponse.SUCCESS