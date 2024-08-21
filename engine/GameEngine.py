import pygame
from mechanics.Vector2D import Vector2D
from mechanics.Space import Space
from mechanics.Mechanics import *
from sprites.Sprite import *
from sprites.GeoSprites import *

class GameEngine:
    def __init__(self):
        self.space=Space()
        self.ship=CircleBody2D(position=Vector2D(0,0),velocity=Vector2D(0,0),mass=1,radius=10)
        my_target=CompositeBody2D()
        my_target.add_body(CircleBody2D(position=Vector2D(100,0),mass=0.25,radius=10))
        my_target.add_body(CircleBody2D(position=Vector2D(110,0),mass=0.25,radius=10))
        my_target.add_body(CircleBody2D(position=Vector2D(100,40),mass=0.25,radius=10))
        my_target.add_body(CircleBody2D(position=Vector2D(110,40),mass=0.25,radius=10))
        self.target=my_target

        #self.target=CircleBody2D(position=Vector2D(100,15),velocity=Vector2D(0,0),mass=1,radius=10)        
        self.space.add_body(self.ship)
        self.space.add_body(self.target)        
        #self.circle_sprite1=CircleSprite()
        #self.circle_sprite2=CircleSprite(color=(255,0,0))

        self.thrust=Vector2D(0,0)    
        self.report_timer=0
        self.report_interval=1000

    def update(self,ticks):
        self.ship.apply_force(self.thrust,self.ship.get_position())
        self.space.update(ticks/1000.0)        
        self.report_timer+=ticks
        if self.report_timer>self.report_interval:
            #print("ship position: ",self.ship.get_position())
            print("target angle: ",self.target.get_angle())
            self.report_timer=0

    def draw(self,screen):
        camera=Camera(screen)
        screen.fill((0,0,0))
        ship_sprite=get_sprite_from_body(self.ship,color=(0,255,0))
        target_sprite=get_sprite_from_body(self.target)
        ship_sprite.blit(screen,camera)
        target_sprite.blit(screen,camera)
        
    def handle_event(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.thrust=Vector2D(10,0)
                
                ...
            if event.key == pygame.K_DOWN:
                ...
            if event.key == pygame.K_LEFT:
                ...
            if event.key == pygame.K_RIGHT:
                ...                                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.thrust=Vector2D(0,0)
                
            if event.key == pygame.K_DOWN:
                ...
            if event.key == pygame.K_LEFT:
                ...                     
            if event.key == pygame.K_RIGHT:
                ...          