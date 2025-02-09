import pygame
import pymunk
from sprites.Sprite import *
from engine.MagnetileShip import *
from gui.DesignerMenus import *

class ShipBuilderEngine:
    def __init__(self,ui_manager):
        self.placement_space = pymunk.Space()
        self.placement_camera=Camera() 
        self.ui_manager=ui_manager
        enemy_choices=["ship1","ship2","ship3","ship4","ship5"]
        self.the_ship=get_ship_factory().get_ship(random.choice(enemy_choices))
        #self.the_ship=MagnetileShip()
        self.selection_window=MagnetileSelection(self.ui_manager)

    def handle_event(self,event):
        return False


    def draw(self,screen):
        self.placement_camera.set_screen(screen)
        screen.fill((0,0,0))

        self.the_ship.get_sprite().blit(screen,self.placement_camera)