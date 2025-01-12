
import pygame
from engine.GameEngine import GameEngine
from gui.GUI import *
from pygame_gui.windows.ui_message_window import UIMessageWindow
from game_state.GameStates import *


class GameState:
    def __init__(self,manager,engine):
        self.is_done=False
        self.next_state_name=None

    def get_done(self):
        return self.is_done
    
    def get_next_state(self):
        return self.next_state_name
    
    def init_state(self):
        print("state "+self.__class__.__name__+" initialized")
        pass

    def finalize_state(self):
        pass

    def update(self,ticks):
        pass

class GameStateManager:
    def __init__(self):
        self.state_dictionary={} #name to state
        self.current_state=None

    def transition_to_state(self,state_name):
        if self.current_state is not None:
            self.current_state.finalize_state()
        self.current_state=self.state_dictionary[state_name]
        self.current_state.init_state()        

    def update(self,ticks):
        if self.current_state is not None:
            self.current_state.update(ticks)
            if self.current_state.get_done():
                self.transition_to_state(self.current_state.get_next_state())
                

class SelectShipState(GameState):
    def __init__(self,manager,engine):        
        super().__init__(manager,engine)
        self.manager=manager
        self.select_ship_window=None
        self.engine=engine
        self.next_state_name=GameStateName.PLAY
    
    def init_state(self):
        super().init_state()

        ship_names=["ship1","ship2","ship3","ship4","ship5"]            
        self.select_ship_window=SelectShipWindow(self.manager,ship_names,self.engine)

    def get_done(self):
        return self.select_ship_window.is_done    
    
class SingleVsMultiState(GameState):
    def __init__(self,manager,engine):
        super().__init__(manager,engine)
        self.manager=manager
        self.engine=engine
        self.next_state_name=GameStateName.SELECT_SHIP

    def init_state(self):
        super().init_state()
        self.single_vs_multi_window=SingleVsMultiplayerSelectWindow(self.manager,self.engine)    
        

    def get_done(self):
        if self.single_vs_multi_window.is_done:
            if self.single_vs_multi_window.next_state_name is not None:
                self.next_state_name=self.single_vs_multi_window.next_state_name
            return True
        return False
    
class MessageWindowState(GameState):
    def __init__(self,manager,engine,message,next_state_name):
        super().__init__(manager,engine)
        self.manager=manager        
        self.engine=engine
        self.message=message
        self.next_state_name=next_state_name

    def init_state(self):
        self.message_window=UIMessageWindow(pygame.Rect(100, 100, 400, 400), self.message,self.manager)

    def get_done(self):
        return not self.message_window.is_enabled



class PlayGameState(GameState):
    def __init__(self,manager,engine):
        super().__init__(manager,engine)
        #self.game_state = GameState.SINGLE_VS_MULTI        
        self.engine=engine
        self.manager=manager

    def update(self,ticks):        
        self.engine.update(ticks)                   