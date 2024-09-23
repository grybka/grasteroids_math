from engine.BehaviorTree import *
from engine.NPC_control import *

class TorpedoBehavior(BehaviorTree):
    def __init__(self,npc,engine):
        children=[]
        data={}
        children.append(SearchForTarget(npc,data,engine,target_name="target"))
        children.append(InterceptShip(npc,"target",data,ideal_velocity=1000))
        self.behavior=SequenceBehavior(children)
        

    def execute(self):
        return self.behavior.execute()        