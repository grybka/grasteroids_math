from enum import Enum

class GameState:
    def __init__(self,state_manager):
        self.state_manager=state_manager
        pass
    
    def init_state(self):
        print("state "+self.__class__.__name__+" initialized")
        pass

    def finalize_state(self):
        print("state "+self.__class__.__name__+" finalized")
        pass

    def draw_state(self,screen):
        #I shouldn't really use this, it should get stuck into a ui pane, but for now...
        pass

    #returns 
    # false, None if not done
    # true, next_state_name if done
    def update(self,ticks):
        return False,None
    
    #return true if event is handled
    def handle_event(self,event):
        return False
    
state_dictionary={} #name to state
    
class GameStateManager:
    def __init__(self,ui_manager):
        self.ui_manager=ui_manager
        self.current_state=None
        self.persistent_data={}

    def transition_to_state(self,state_name):
        if state_name not in state_dictionary:
            print("state "+state_name+" not found")
            return
        state=state_dictionary[state_name]
        if self.current_state is not None:
            self.current_state.finalize_state()
        self.current_state=state(self)
        if self.current_state is not None:
            self.current_state.init_state()        
        else:
            print("state is None")
    
    def update(self,ticks):
        if self.current_state is not None:
            done,next_state_name=self.current_state.update(ticks)
            if done:
                self.transition_to_state(next_state_name)

    def draw_state(self,screen):
        if self.current_state is not None:
            self.current_state.draw_state(screen)

    def handle_event(self,event):
        if self.current_state is not None:
            return self.current_state.handle_event(event)
        return False