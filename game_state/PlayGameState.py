
import pygame
from engine.GameEngine import GameEngine
from gui.GUI import *
from pygame_gui.windows.ui_message_window import UIMessageWindow
from game_state.GameState import *
from pygame_gui._constants import UI_WINDOW_CLOSE
from engine.GameEngine import GameEngine




class PlayGameState(GameState):
    def __init__(self,state_manager):
        super().__init__(state_manager)
        #self.menu_window=UIMessageWindow(pygame.Rect(100, 100, 400, 400), "MainMenu", state_manager.ui_manager)
        #self.is_done=False
        self.engine=GameEngine()
        #self.engine.set_controller(controller)


    def init_state(self):
        super().init_state()
        if self.state_manager.persistent_data["game_mode"]=="single":
            controller = pygame.joystick.Joystick(0)
            self.engine.set_controller(controller)
            self.engine.spawn_player("ship1")
        else:
            self.engine.spawn_player("ship1")

        #self.menu_window.show()

    def update(self,ticks):       
        self.engine.update(ticks)
        #if self.is_done:
            #self.menu_window.hide()
            #return True,"PlayGameState"
        return False,None
    
    def draw_state(self,screen):
        self.engine.draw(screen)
    
    def handle_event(self,event):
        return self.engine.handle_event(event)       
#        return False

state_dictionary["PlayGameState"]=PlayGameState

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
                  