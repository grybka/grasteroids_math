from enum import Enum

class GameState:
    def __init__(self):
        pass
    
    def init_state(self):
        print("state "+self.__class__.__name__+" initialized")
        pass

    def finalize_state(self):
        print("state "+self.__class__.__name__+" finalized")
        pass

    #returns 
    # false, None if not done
    # true, next_state_name if done
    def update(self,ticks):
        return False,None
    
    #return true if event is handled
    def handle_event(self,event):
        return False
    
class GameStateManager:
    def __init__(self):
        self.current_state=None

    def transition_to_state(self,state):
        if self.current_state is not None:
            self.current_state.finalize_state()
        self.current_state=state
        if self.current_state is not None:
            self.current_state.init_state()        
        else:
            print("state is None")
    
    def update(self,ticks):
        if self.current_state is not None:
            done,next_state_name=self.current_state.update(ticks)
            if done:
                self.transition_to_state(next_state_name)

    def handle_event(self,event):
        if self.current_state is not None:
            return self.current_state.handle_event(event)
        return False