from engine.Enums import *




class BehaviorTree:
    def __init__(self,npc=None,data={}):
        self.npc=npc #npc is the object that the behavior tree is controlling
        self.data=data        

    def execute(self):
        return BTreeResponse.FAILURE
    
#execute children in order until one fails, then return failure
class SequenceBehavior(BehaviorTree):
    def __init__(self,children=[]):
        self.children=children

    def add_child(self,child):
        self.children.append(child)

    def execute(self):
        for child in self.children:
            result=child.execute()
            if result==BTreeResponse.FAILURE:
                return BTreeResponse.FAILURE
            if result==BTreeResponse.RUNNING:
                return BTreeResponse.RUNNING
        return BTreeResponse.SUCCESS
    
#execute children in order until one succeeds, then return success
class SelectorBehavior(BehaviorTree):
    def __init__(self,children=[]):
        self.children=children

    def add_child(self,child):
        self.children.append(child)

    def execute(self):
        for child in self.children:
            result=child.execute()
            if result==BTreeResponse.SUCCESS:
                return BTreeResponse.SUCCESS
            if result==BTreeResponse.RUNNING:
                return BTreeResponse.RUNNING
        return BTreeResponse.FAILURE
    
#execute all children in parallel and return success only if all children return success
#return failure if any child returns failure
class ParallelBehavior(BehaviorTree):
    def __init__(self,children=[]):
        self.children=children

    def add_child(self,child):
        self.children.append(child)

    def execute(self):        
        any_running=False
        any_failed=False
        for child in self.children:
            result=child.execute()
            if result==BTreeResponse.FAILURE:
                any_failed=True                
            if result==BTreeResponse.RUNNING:
                any_running=True
        if any_failed:
            return BTreeResponse.FAILURE                
        if any_running:
            return BTreeResponse.RUNNING
        return BTreeResponse.SUCCESS
    
class DoOnce(BehaviorTree):
    def __init__(self,child):
        self.child=child
        self.has_succeeded=False

    def execute(self):
        if self.has_succeeded:
            return BTreeResponse.SUCCESS
        result=self.child.execute()
        if result==BTreeResponse.SUCCESS:
            self.has_succeeded=True
        return result