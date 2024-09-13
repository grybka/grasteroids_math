import pygame
import pygame_gui

from pygame_gui.elements.ui_window import UIWindow

class SelectShipWindow(UIWindow):
    def __init__(self, ui_manager: pygame_gui.UIManager):
        self.ui_manager = ui_manager
        
    def process_event(self, event):
        handled = super().process_event(event)
        return handled
    
    def update(self, time_delta):
        ...

    
        
    