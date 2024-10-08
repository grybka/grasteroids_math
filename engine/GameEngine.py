import pygame
from mechanics.Vector2D import Vector2D
from mechanics.Space import Space
from mechanics.Mechanics import *
from sprites.Sprite import *
from sprites.GeoSprites import *
from engine.GameObjects import *

class GameEngine:
    def __init__(self,clock):
        self.clock=clock
        self.space=Space()
        self.ship=CircleBody2D(position=Vector2D(0,0),velocity=Vector2D(0,0),mass=1,radius=10)
        #self.ship=SquareBody2D(position=Vector2D(0,19),mass=1,radius=10,angle=0)
        #self.ship=EquilateralTriangleBody2D(radius=10)
        self.ship.set_velocity(Vector2D(20,0))
        #target_triangle=SquareBody2D(position=Vector2D(100,0),mass=1,radius=20,angle=0)
        #my_target=CompositeBody2D()
        #my_target.add_body(CircleBody2D(position=Vector2D(100,0),mass=0.25,radius=10))
        #my_target.add_body(CircleBody2D(position=Vector2D(140,0),mass=0.25,radius=10))
        #my_target.add_body(CircleBody2D(position=Vector2D(100,40),mass=0.25,radius=10))
        #my_target.add_body(CircleBody2D(position=Vector2D(140,40),mass=0.25,radius=10))
        #self.target=my_target
        #self.target=target_triangle
        self.target=Asteroid()
        self.target.set_position(Vector2D(100,0))

        #self.target=CircleBody2D(position=Vector2D(100,15),velocity=Vector2D(0,0),mass=1,radius=10)        
        self.space.add_body(self.ship)
        self.space.add_body(self.target)        
        #self.circle_sprite1=CircleSprite()
        #self.circle_sprite2=CircleSprite(color=(255,0,0))

        self.thrust=Vector2D(0,0)    
        self.report_timer=0
        self.report_interval=2000

    def update(self,ticks):
        if self.thrust.magnitude()>0:
            self.ship.apply_force(self.thrust,self.ship.get_position())
        self.space.update(ticks/1000.0)        
        self.report_timer+=ticks
        if self.report_timer>self.report_interval:
            #print("ship position: ",self.ship.get_position())
            #print("target angle: ",self.target.get_angle())
            #print("target position: ",self.target.get_position())  
            #print("target moment of inertia: ",self.target.moment_of_inertia)
            #print("target mass ",self.target.mass)
            print("fps: ",self.clock.get_fps())
            self.report_timer=0

    def draw(self,screen):
        camera=Camera(screen)
        screen.fill((0,0,0))
        ship_sprite=get_sprite_from_body(self.ship,color=(0,255,0))
        #target_sprite=get_sprite_from_body(self.target)
        ship_sprite.blit(screen,camera)
        #target_sprite.blit(screen,camera)
        self.target.get_sprite().blit(screen,camera)
        
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