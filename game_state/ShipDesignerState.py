
from game_state.GameState import *
from engine.ShipBuilderEngine import *


class ShipDesignerState(GameState):
    def __init__(self,state_manager):
        super().__init__(state_manager)


    def init_state(self):
        super().init_state()
        self.engine=ShipBuilderEngine(self.state_manager.ui_manager)

    
    def update(self,ticks):  
        return False,None
    
     
    def draw_state(self,screen):
        self.engine.draw(screen)
        
    def handle_event(self,event):
        return self.engine.handle_event(event)
    
state_dictionary["ShipDesignerState"]=ShipDesignerState
