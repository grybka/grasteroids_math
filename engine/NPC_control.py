from enum import Enum
from engine.Ship import PointingNavigationMode, VelocityNavigationMode



#Unaware ships
#Pick a random point in space
#Fly towards it
#if you see the player ship, chase it

#Aware ships
#I want to be pointing towards player ship
#when there's a decent chance of hitting it, fire

class BTreeResponse(Enum):
    SUCCESS=1
    FAILURE=2
    RUNNING=3


class BehaviorTree:
    def __init__(self):
        ...

    def execute(self):
        return BTreeResponse.FAILURE
    
class TurnTowardsPlayer(BehaviorTree):
    def __init__(self,npc,player,angle_threshold=0.1):
        self.npc=npc
        self.player=player
        self.angle_threshold=angle_threshold

    def execute(self):
        desired_direction=self.player.body.position-self.npc.body.position
        current_angle=self.npc.body.angle
        if abs(desired_direction.angle-current_angle)<self.angle_threshold:
            return BTreeResponse.SUCCESS
        self.npc.set_desired_direction(self.player.body.position-self.npc.body.position)
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        
        return BTreeResponse.RUNNING
    
class MoveToPoint(BehaviorTree):
    def __init__(self,npc,point,point_threshold=5):
        self.npc=npc
        self.point=point
        self.point_threshold=point_threshold

    def execute(self):
        desired_direction=self.point-self.npc.body.position
        if desired_direction.length<self.point_threshold:
            return BTreeResponse.SUCCESS
        self.npc.set_desired_direction(desired_direction)
        self.npc.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)                        
        return BTreeResponse.RUNNING
    

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