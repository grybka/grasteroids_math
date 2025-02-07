from engine.Enums import *
from pymunk import Vec2d
import math
import random 
from behavior_tree.BehaviorTree import *

#if target locket
#point towards target
#fire
#else
#scan for target

def angle_subtract(a,b):
    x=a-b
    while x>math.pi:
        x-=2*math.pi
    while x<-math.pi:
        x+=2*math.pi
    return x

class DefaultTurretBehavior(BehaviorTree):
    def __init__(self,npc,engine,data={}):
        super().__init__(npc,data)
        self.engine=engine
        #in this case, NPC is a turret

    def execute(self):
        ...

class TurretBehaviorScan(BehaviorTree):
    def __init__(self,npc,engine,data={}):
        super().__init__(npc,data)
        self.engine=engine
        #in this case, NPC is a turret
        self.scan_direction=1
        self.scan_speed=0.025

    def execute(self):     
        self.npc.angle+=self.scan_direction*self.scan_speed
        if self.npc.angle>self.npc.max_angle:
            self.scan_direction=-1
            self.npc.angle=self.npc.max_angle   
        if self.npc.angle<self.npc.min_angle:
            self.scan_direction=1
            self.npc.angle=self.npc.min_angle  
        return BTreeResponse.SUCCESS      

class TurretSearchForTarget(BehaviorTree):
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

#success is returned if the turret is able to fire
class TurretBehaviorFireOnTarget(BehaviorTree):
    def __init__(self,npc,engine,data={}):
        super().__init__(npc,data)
        self.engine=engine
        self.angle_accuracy=0.1

    def execute(self):
        if self.target_name not in self.data:
            return BTreeResponse.FAILURE
        target=self.data[self.target_name]
        dx=target.body.position-self.npc.body.position
