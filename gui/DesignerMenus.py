import pygame
import pygame_gui

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.windows.ui_colour_picker_dialog import UIColourPickerDialog
from pygame_gui.elements import UIImage,UIButton,UIPanel,UIScrollingContainer,UITextBox
from engine.Magnetile import *
from engine.ShipParts import *

class MagnetileSelection(UIPanel):
    def __init__(self, ui_manager: pygame_gui.UIManager, ship_builder_engine,parent=None,anchors=None):
        #super().__init__(pygame.Rect(0,0,200,600), ui_manager, window_display_title='Magnetile Selection')
        super().__init__(pygame.Rect(0,0,200,600), 1,ui_manager,parent_element=parent,container=parent,anchors=anchors)
        self.ship_builder_engine=ship_builder_engine
        self.choices=[]
        self.choices.append(SquareMagnetile())
        self.choices.append(RectMagnetile())
        self.choices.append(TallRightTriangleMagnetile())
        self.choices.append(IsocelesTriangleMagnetile())
        self.choices.append(EquilateralTriangleMagnetile())


        contents=UIScrollingContainer(relative_rect=pygame.Rect(0, 0, 200, 350),manager=self.ui_manager,container=self,should_grow_automatically=False)
        self.pick_color_button=UIButton(relative_rect=pygame.Rect(5, 5, 100, 30),
                                     text='Pick Color',
                                     manager=ui_manager,
                                     container=self,anchors={"left":"left","top_target":contents})
        self.set_color_button=UIButton(relative_rect=pygame.Rect(5, 5, 100, 30),
                                     text='Set Color',
                                     manager=ui_manager,
                                     container=self,anchors={"left_target":self.pick_color_button,"top_target":contents})
        self.selections=[]
        last_choice=None
        for choice in self.choices:
            length_scale=60
            image_size=(64,64)        
            image_surface=pygame.surface.Surface(image_size)
            image_surface.fill((0,0,0))
            camera=Camera()
            camera.set_screen(image_surface)
            camera.zoom=image_size[0]/(2*length_scale)
            choice.get_sprite().blit(image_surface,camera)
            if last_choice is not None:
                anchors={"centerx":"centerx",
                                 'top_target': last_choice}
            else:
                anchors={"centerx":"centerx",
                                 'top':"top"}

            ship_image=UIImage(relative_rect=pygame.Rect(5, 5, image_size[0],image_size[1]),
                        image_surface=image_surface,
                        manager=self.ui_manager,
                        container=contents,
                        anchors=anchors)
            self.selections.append(ship_image)
            last_choice=ship_image
        self.set_current_color(pygame.Color(255, 0, 0, 255))
    
        
    def set_current_color(self,color):
        self.current_colour=color
        for i in range(len(self.choices)):     
            print(i)   
            choice=self.choices[i]
            choice.set_color(color)        
            length_scale=60
            image_size=(64,64)        
            image_surface=pygame.surface.Surface(image_size)
            image_surface.fill((0,0,0))
            camera=Camera()
            camera.set_screen(image_surface)
            camera.zoom=image_size[0]/(2*length_scale)
            choice.get_sprite().blit(image_surface,camera)    
            self.selections[i].set_image(image_surface)

    def process_event(self, event):
        handled = super().process_event(event)
        if event.type==pygame.MOUSEBUTTONDOWN:
            for i,selection in enumerate(self.selections):
                if selection.rect.collidepoint(event.pos):
                    print("clicked on {}".format(self.choices[i]))
                    self.ship_builder_engine.magnetile_selected(self.choices[i])
                    #self.ui_manager.get_root_container().set_selected_magnetile(self.choices[i])
                    return True      
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.pick_color_button:    
                self.colour_picker = UIColourPickerDialog(pygame.Rect(160, 50, 420, 400),
                                                              self.ui_manager,
                                                              window_title='Change Colour...',
                                                              initial_colour=self.current_colour)
                self.colour_picker.set_blocking(True)
                return True
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.set_color_button:
                ...
                #TODO set color
                return True

        if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                self.set_current_color(event.colour)
                #TODO change magnetile color                    
                return True
        if (event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.colour_picker):
                self.colour_picker = None

        return handled
    

class ComponentSelection(UIPanel):
    def __init__(self, ui_manager: pygame_gui.UIManager, ship_builder_engine,parent=None,anchors=None):
        super().__init__(pygame.Rect(0,0,200,600), 1,ui_manager,parent_element=parent,container=parent,anchors=anchors)
        self.ship_builder_engine=ship_builder_engine
        self.button_names=["Cannon","Torpedo Tube","Cannon Turret"]
        self.buttons=[]
        for name in self.button_names:
            self.buttons.append(UIButton(relative_rect=pygame.Rect(5, 5, 100, 30),
                                         text=name,
                                            manager=ui_manager,
                                            container=self,anchors={"left":"left","top_target":self.buttons[-1]} if len(self.buttons)>0 else {"left":"left","top":"top"}))
    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.buttons:
                button_index=self.buttons.index(event.ui_element)
                print("button index was {}".format(button_index))
                print("clicked on {}".format(self.button_names[button_index]))
                if self.button_names[button_index]=="Cannon Turret":
                    self.ship_builder_engine.turret_selected()

                    ...
                    #self.ship_builder_engine.add_component(Cannon())
                return True
        return handled
    


class MagnetileDesigner(UIWindow):
    def __init__(self, ui_manager: pygame_gui.UIManager, ship_builder_engine):
        super().__init__(pygame.Rect(0,0,400,1200), ui_manager, window_display_title='Designer')
        
        self.tile_button=UIButton(relative_rect=pygame.Rect(5, 5, 100, 30),
                                     text='Tiles',
                                     manager=ui_manager,
                                     container=self,anchors={"left":"left","top":"top"})
        self.component_button=UIButton(relative_rect=pygame.Rect(5, 5, 100, 30),
                                     text='Components',
                                     manager=ui_manager,
                                     container=self,anchors={"left_target":self.tile_button})
        self.magnetile_selection=MagnetileSelection(ui_manager,ship_builder_engine,self,anchors={"left":"left","top_target":self.component_button})
        self.magnetile_selection.hide()
        self.component_selection=ComponentSelection(ui_manager,ship_builder_engine,self,anchors={"left":"left","top_target":self.component_button})
        self.component_selection.hide()
        self.active_panel=None

    def process_event(self, event):
        handled = super().process_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.tile_button:
                if self.active_panel is not None:
                    self.active_panel.hide()
                self.active_panel=self.magnetile_selection
                self.active_panel.show()                  
                return True
            if event.ui_element == self.component_button:
                if self.active_panel is not None:
                    self.active_panel.hide()
                self.active_panel=self.component_selection                
                self.active_panel.show()                  
                return True
        return handled