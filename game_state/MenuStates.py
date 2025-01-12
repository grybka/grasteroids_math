from game_state.GameState import *
import pygame
from pygame_gui import UIManager
from pygame_gui.windows.ui_message_window import UIMessageWindow
from pygame_gui._constants import UI_WINDOW_CLOSE

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