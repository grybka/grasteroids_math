from behavior_tree.BehaviorTree import *
from behavior_tree.NPC_control import *

class TorpedoBehavior(BehaviorTree):
    def __init__(self,npc,engine):
        children=[]
        data={}
        children.append(SearchForTarget(npc,data,engine,target_name="target"))
        children.append(InterceptShip(npc,"target",data,ideal_velocity=1400))
        self.behavior=SequenceBehavior(children)
        

    def execute(self):
        return self.behavior.execute()        
    
class AggressiveBehavior(BehaviorTree):
    def __init__(self,npc,engine):
        children=[]
        data={}
        fight=SequenceBehavior([SearchForTarget(npc,data,engine,target_name="target"),ApproachToDistance(npc,"target",data,distance=1500),ZeroVelocity(npc),FireAtPlayer(npc,"target",data,fire_threshold=0.1)])                                
        
        self.behavior=SelectorBehavior([fight,WanderRandomly(npc,arena_size=(-2000,-2000,4000,4000),timescale=60)])

    def execute(self):
        return self.behavior.execute()        