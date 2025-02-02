from game_state.GameState import GameState, state_dictionary
import pygame
from pygame_gui import UIManager,UI_WINDOW_CLOSE
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui._constants import UI_WINDOW_CLOSE

from gui.Menus import *

class MainMenuState(GameState):
    def __init__(self,state_manager):
        super().__init__(state_manager)
        #self.menu_window=UIMessageWindow(pygame.Rect(100, 100, 400, 400), "MainMenu", state_manager.ui_manager)
        self.menu_window=TitleMenuWindow(state_manager.ui_manager,state_manager)
        self.is_done=False

    def init_state(self):
        super().init_state()
        self.menu_window.show()

    def update(self,ticks):        
#        if self.is_done:
        if self.menu_window.start_game:
            self.menu_window.hide()
            return True,"PlayGameState"
        return False,None
    
    def handle_event(self,event):
        #if event.type == UI_WINDOW_CLOSE:
        #    print("window closed")
        #    if event.ui_element == self.menu_window:
        #        print("my window!")
        #        self.is_done=True
        return False

state_dictionary["MainMenuState"]=MainMenuState

class GameOverState(GameState):
       def __init__(self,state_manager):
        super().__init__(state_manager)
        self.menu_window=GameOverWindow(state_manager.ui_manager,state_manager)
        self.is_done=False

    def init_state(self):
        super().init_state()
        self.menu_window.show()

    def update(self,ticks):        
#        if self.is_done:
        if self.menu_window.start_game:
            self.menu_window.hide()
            return True,"MainMenuState"
        return False,None
    
    def handle_event(self,event):
        #if event.type == UI_WINDOW_CLOSE:
        #    print("window closed")
        #    if event.ui_element == self.menu_window:
        #        print("my window!")
        #        self.is_done=True
        return False

state_dictionary["GameOverState"]=GameOverState



class ConfirmDialogState(GameState):
    def __init__(self,message,next_state=None):
        super().__init__()        
        self.menu_window=UIMessageWindow(pygame.Rect(100, 100, 400, 400), UIManager(), message)
        self.is_done=False     
        self.next_state=next_state
    
    def init_state(self):
        super().init_state()
        self.menu_window.show()

    def update(self,ticks):        
        if self.menu_window.is_done:
            self.menu_window.hide()
            return True,self.next_state
        return False,None
    
    def handle_event(self, event):
        if event.type==UI_WINDOW_CLOSE:
            if event.ui_element==self.menu_window:
                self.is_done=True
                return True            
        return super().handle_event(event)