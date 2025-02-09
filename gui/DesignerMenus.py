import pygame
import pygame_gui

from pygame_gui.elements.ui_window import UIWindow
from pygame_gui.elements import UIImage,UIButton,UIPanel,UIScrollingContainer,UITextBox
from engine.Magnetile import *

class MagnetileSelection(UIWindow):
    def __init__(self, ui_manager: pygame_gui.UIManager):
        super().__init__(pygame.Rect(0,0,200,600), ui_manager, window_display_title='Magnetile Selection')
        self.choices=[]
        self.choices.append(SquareMagnetile())
        self.choices.append(RectMagnetile())
        self.choices.append(TallRightTriangleMagnetile())
        self.choices.append(IsocelesTriangleMagnetile())
        self.choices.append(EquilateralTriangleMagnetile())


        contents=UIScrollingContainer(relative_rect=pygame.Rect(0, 0, 200, 350),manager=self.ui_manager,container=self,should_grow_automatically=False)
        self.selections=[]
        last_choice=None
        for choice in self.choices:
            length_scale=40
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

    def process_event(self, event):
        handled = super().process_event(event)
        if event.type==pygame.MOUSEBUTTONDOWN:
            #self.ui_manager.get_mouse_position()
            mpos=self.get_relative_mouse_pos()

        print("event is {}".format(event))
        return handled