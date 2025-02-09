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

#success is returned if the turret is able to fire
class TurretBehaviorFireOnTarget(BehaviorTree):
    def __init__(self,npc,engine,target_angle,data={}):
        super().__init__(npc,data)
        self.engine=engine
        self.angle_accuracy=0.1
        self.target_angle=target_angle

    def execute(self):
        #print("Firing on target")
        #print(self.npc.get_world_angle())
        #print(self.target_angle)

        if abs(self.npc.get_world_angle()-self.target_angle)<self.angle_accuracy:
            self.npc.fire_weapon()
            #print("Firing")
            return BTreeResponse.SUCCESS
        else:
            if angle_subtract(self.npc.get_world_angle(),self.target_angle)>0:
                self.npc.angle-=0.1
            else:
                self.npc.angle+=0.1
        
class DefaultTurretBehavior(BehaviorTree):
    def __init__(self,npc,engine,data={}):
        super().__init__(npc,data)
        self.engine=engine

        self.scan_behavior=TurretBehaviorScan(npc,data,engine)
        #in this case, NPC is a turret

    def execute(self):
        #TODO Fix this angle handling, it's too wide a cone
#        objs=self.engine.get_objects_in_cone(self.npc.get_position(),self.npc.get_world_mount_angle(),math.pi/4,1000,filter=None)
        objs=self.engine.get_ships_in_cone(self.npc.get_position(),self.npc.get_world_mount_angle(),math.pi/4,1000)

        if len(objs)!=0:
            target=objs[0]
            #get the angle to the target
            dx=target.body.position-self.npc.get_position()            
            angle_to_target=angle_subtract(dx.angle,math.pi/2)
            self.npc.set_angle_to_world_angle(angle_to_target)                                              
            #print("angle to target {}".format(angle_to_target))
            firebehavior=TurretBehaviorFireOnTarget(self.npc,self.engine,angle_to_target)
            firebehavior.execute()
        else:
            self.scan_behavior.execute()
            #print("no target")

        
            

        ...