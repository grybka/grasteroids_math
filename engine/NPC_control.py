from enum import Enum
from engine.Ship import PointingNavigationMode, VelocityNavigationMode, ControllableShip
from pymunk import Vec2d
import math
import random 
from engine.BehaviorTree import *

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
    def __init__(self,npc: ControllableShip, point,angle_threshold=0.1):
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
    def __init__(self,npc: ControllableShip ,point,point_threshold=5):
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
    def __init__(self,npc,player,fire_threshold=0.1):
        self.npc=npc
        self.player=player
        self.fire_threshold=fire_threshold

    def execute(self):
        desired_direction=self.player.body.position-self.npc.body.position            
        delta_angle=angle_subtract(desired_direction.angle-math.pi/2,self.npc.body.angle)

        if abs(delta_angle)<self.fire_threshold:
            self.npc.set_firing(True)
            #print("fire")
            return BTreeResponse.SUCCESS
        #print("delta_angle",delta_angle)
        
        self.npc.set_firing(False)
        self.npc.set_desired_direction(self.player.body.position-self.npc.body.position)
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        
        return BTreeResponse.RUNNING

class WanderRandomly(BehaviorTree):
    def __init__(self,npc,arena_size=(-2000,-2000,4000,4000),timescale=20*60):
        self.npc=npc
        self.arena_size=arena_size
        self.target=Vec2d(0,0)
        self.timescale=timescale
        self.time_since_last_target=timescale

    def execute(self):
        self.time_since_last_target+=1
        if self.time_since_last_target>self.timescale:          
            self.target=Vec2d(self.arena_size[0]+self.arena_size[2]*random.random(),self.arena_size[1]+self.arena_size[3]*random.random())
            print("New wander target",self.target)
            self.time_since_last_target=0
        if MoveToPoint(self.npc,self.target).execute()==BTreeResponse.SUCCESS:
            self.time_since_last_target=self.timescale
        return BTreeResponse.RUNNING
    
class InterceptShip(BehaviorTree):
    def __init__(self,npc,ship,ideal_velocity=1000):
        self.npc=npc
        self.ship=ship
        self.ideal_velocity=ideal_velocity #magnitude

    def execute(self):
        #turn_part=TurnTowardsPlayer(self.npc,self.ship).execute()
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        

        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY) 
        dx=self.ship.body.position-self.npc.body.position
        current_velocity=self.npc.body.velocity
#        ideal_velocity_mag=min(self.ideal_velocity,current_velocity.length*1.1)
        ideal_velocity_mag=self.ideal_velocity
        target_velocity=ideal_velocity_mag*dx.normalized()+self.ship.body.velocity
        self.npc.set_desired_velocity(target_velocity)
        
        dv=target_velocity-current_velocity
        self.npc.set_desired_direction(dv.normalized())


        return BTreeResponse.RUNNING           




#Needs rework below

class ApproachToDistance(BehaviorTree):
    def __init__(self,npc,player,too_close=100,too_far=200):
        self.npc=npc
        self.player=player
        self.too_close=too_close
        self.too_far=too_far
        self.op1=ApproachTarget(npc,player,success_radius=too_close,ideal_velocity=1000)
        self.op2=AvoidTarget(npc,player,success_radius=too_far,ideal_velocity=1000)
        

    def execute(self):
        if self.op1.execute()==BTreeResponse.SUCCESS:
            return BTreeResponse.SUCCESS
        if self.op2.execute()==BTreeResponse.SUCCESS:
            return BTreeResponse.SUCCESS
        return BTreeResponse.RUNNING
        
    
class ApproachTarget(BehaviorTree):
    def __init__(self,npc,target,success_radius=5,ideal_velocity=1000):
        self.npc=npc
        self.target=target
        self.success_radius=success_radius
        self.ideal_velocity=ideal_velocity

    def execute(self):
        dx=self.target.body.position-self.npc.body.position
        if dx.length<self.success_radius:
            return BTreeResponse.SUCCESS
        #TODO Figure out what this velocity is
        self.npc.set_desired_velocity(self.ideal_velocity*dx.normalized()+self.target.body.velocity)
        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)
        self.npc.set_desired_direction(self.target.body.position-self.npc.body.position)
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)
        return BTreeResponse.RUNNING
        
class AvoidTarget(BehaviorTree):
    def __init__(self,npc,target,success_radius=5,ideal_velocity=1000):
        self.npc=npc
        self.target=target
        self.success_radius=success_radius
        self.ideal_velocity=ideal_velocity

    def execute(self):
        dx=self.target.body.position-self.npc.body.position
        if dx.length>self.success_radius:
            return BTreeResponse.SUCCESS
        #TODO Figure out what this velocity is
        self.npc.set_desired_velocity(-self.ideal_velocity*dx.normalized()+self.target.body.velocity)
        self.npc.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)
        self.npc.set_desired_direction(-self.target.body.position+self.npc.body.position)
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)
        return BTreeResponse.RUNNING