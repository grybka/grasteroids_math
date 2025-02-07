import pygame
import pygame_gui

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements import UIImage,UIButton,UIPanel,UIScrollingContainer,UITextBox
from engine.MagnetileShip import get_ship_factory
from sprites.Sprite import Camera

from enum import Enum

class TitleMenuWindowSelection(Enum):
    NOTHING=0
    SINGLE_PLAYER=1
    OBSERVER=2

class TitleMenuWindow(UIWindow):
    def __init__(self, ui_manager: pygame_gui.UIManager,state_manger):
        root=ui_manager.get_root_container()
        root_rect=root.get_rect()
        print("root rect is {}".format(root_rect))
        super().__init__(root_rect, ui_manager, window_display_title='')
        width=root_rect[2]
        center_y=root_rect[3]/2
        #super().__init__(root.get_rect(), ui_manager)
        #button_rect=root_rect.inflate(-400,-400)
        button_rect=pygame.Rect(0,50,200,100)
        print("button rect is {}".format(button_rect))
        self.title_text=UITextBox(relative_rect=pygame.Rect(100,100,width-200,100),
                                  html_text="Magnetile Galaxy",
                                  manager=self.ui_manager,
                                  container=self,object_id="#gametitle",
                                  anchors={"left":"left",
                                             "right":"right",
                                             'top':"top"})
        self.singleplayer_button=UIButton(relative_rect=button_rect,
                        text="SinglePlayer",
                        manager=self.ui_manager,
                        container=self,
                        anchors={"centerx":"centerx",
                                 'top_target': self.title_text})
        self.observer_button=UIButton(relative_rect=button_rect,
                        text="Observer",
                        manager=self.ui_manager,
                        container=self,
                        anchors={"centerx":"centerx",
                                 'top_target': self.singleplayer_button})
        
        #self.start_game=False
        self.selection=TitleMenuWindowSelection.NOTHING
        
        
    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.singleplayer_button:
                print('Start button pressed')
                self.selection=TitleMenuWindowSelection.SINGLE_PLAYER
                #self.start_game=True
                handled=True
            if event.ui_element == self.observer_button:
                print('Start button pressed')
                self.selection=TitleMenuWindowSelection.OBSERVER
                #self.start_game=True
                handled=True
        return handled
    


class GameOverWindow(UIWindow):
    def __init__(self, ui_manager: pygame_gui.UIManager,state_manger):
        root=ui_manager.get_root_container()
        root_rect=root.get_rect()
        super().__init__(root_rect, ui_manager, window_display_title='')
        width=root_rect[2]
        center_y=root_rect[3]/2
        #super().__init__(root.get_rect(), ui_manager)
        button_rect=root_rect.inflate(-400,-400)
        self.start_button=UIButton(relative_rect=button_rect,
                        text="Restart",
                        manager=self.ui_manager,
                        container=self)
        self.title_text=UITextBox(relative_rect=pygame.Rect(100,100,width-200,100),
                                  html_text="Oh No You Explode!",
                                  manager=self.ui_manager,
                                  container=self,object_id="#gametitle")
        self.start_game=False
        
    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                print('Start button pressed')
                self.start_game=True
                handled=True
        return handled