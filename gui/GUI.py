import pygame
import pygame_gui

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements import UIImage,UIButton,UIPanel,UIScrollingContainer
from engine.MagnetileShip import get_ship_factory
from sprites.Sprite import Camera

class ShipSelectPane(UIPanel):
    def __init__(self, ui_manager: pygame_gui.UIManager,ship_name,engine,container=None,top_offset=0):
        width=200
        super().__init__(pygame.Rect(0, top_offset, width, 70), manager=ui_manager, container=container)
        self.ui_manager = ui_manager
        self.engine=engine
        self.ship_name=ship_name
        #image showing the ship
        image_size=(64,64)        
        ship=get_ship_factory().get_ship(ship_name)
        sprite=ship.get_sprite()
        bbox=ship.get_bbox()
        length_scale=max(abs(bbox[2]),abs(bbox[0]),abs(bbox[3]),abs(bbox[1]))
        image_surface=pygame.surface.Surface(image_size)
        image_surface.fill((0,0,0))
        camera=Camera()
        camera.set_screen(image_surface)
        camera.zoom=image_size[0]/(2*length_scale)
        sprite.blit(image_surface,camera)

        self.ship_image=UIImage(relative_rect=pygame.Rect(5, 5, image_size[0],image_size[1]),
                        image_surface=image_surface,
                        manager=self.ui_manager,
                        container=self)   
        
        self.select_button=UIButton(relative_rect=pygame.Rect(image_size[0]+10, 5, width-image_size[0]-10, 20),
                        text="Select",
                        manager=self.ui_manager,
                        container=self)




        #ship=get_ship_factory().get_ship(ship_name)
        #self.ship=ship
        #self.ship_info=ship.get_info()     
        # 
    def process_event(self, event):
        handled = super().process_event(event)   
        #if event.type == pygame_gui.UI_BUTTON_PRESSED:
            #if event.ui_element == self.select_button:
                #print('Selected ship: '+self.ship_name)              
                #self.engine.spawn_player(self.ship_name)
                #handled=True
        return handled
        


class SelectShipWindow(UIWindow):
    def __init__(self, ui_manager: pygame_gui.UIManager,ship_names,engine):
        super().__init__(pygame.Rect(100, 100, 400, 400), ui_manager, window_display_title='Select Ship')
        self.ui_manager = ui_manager
        #button_layout_rect = pygame.Rect(30, 20, 100, 20)
        #ship_factory=get_ship_factory()
        self.buttons=[]
        self.ship_names=ship_names
        self.engine=engine
        button_size=(64,64)
        #button_layout_rect = pygame.Rect(30, 20, button_size[0],button_size[1])
        contents=UIScrollingContainer(relative_rect=pygame.Rect(0, 0, 400, 350),manager=self.ui_manager,container=self,should_grow_automatically=False)
        self.choices=[]
        
        top_offset=10
        for name in ship_names:            
            panel=ShipSelectPane(ui_manager,name,engine,container=contents,top_offset=top_offset)
            self.choices.append(panel)
            top_offset+=panel.get_relative_rect().height+10
        contents.set_scrollable_area_dimensions((300, top_offset))
        
    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for choice in self.choices:
                if event.ui_element == choice.select_button:
                    print('Selected ship: '+choice.ship_name)              
                    self.engine.spawn_player(choice.ship_name)
                    handled=True
                    self.kill()                                             
        return handled
    
    def update(self, time_delta):
        
    
        ...

    
        
    