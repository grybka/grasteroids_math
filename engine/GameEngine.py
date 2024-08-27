import pygame
from sprites.Sprite import *
from engine.GameObjects import *
from engine.Ship import *
import pymunk

class GameEngine:
    def __init__(self,clock):
        self.controller=None

        self.clock=clock
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        self.objects =[]
        self.decorators =[]
        ...
        self.report_timer=0
        self.report_interval=2000
        ...
        #self.my_ship=SquareMagnetile()
        self.my_ship=Ship()
        self.add_object(self.my_ship)
        #self.add_object(SquareMagnetile(position=Vec2d(0,100)))
        ...
        self.desired_velocity=Vec2d(0,0)

    def add_object(self,obj):
        self.space.add(obj.body,obj.shape)
        self.objects.append(obj)

    def add_decorator(self,dec):
        self.decorators.append(dec)

    def update_controls(self):
        if self.controller is not None:
                axis_dead_zone=0.15
                #left stick
                axis0=self.controller.get_axis(0)  
                axis1=self.controller.get_axis(1)  
                if abs(axis0)>axis_dead_zone or abs(axis1)>axis_dead_zone:
                    ...                
                #right stick
                axis2=self.controller.get_axis(2)
                axis3=self.controller.get_axis(3)

                if abs(axis2)>axis_dead_zone or abs(axis3)>axis_dead_zone:
                    ...

    def update(self,ticks):
        #update controls
        self.update_controls()        

        #update objects
        for obj in self.objects:
            obj.update(ticks,self)     

        #update physics        
        self.space.step(ticks/1000.0)        

        #update decorators
        for dec in self.decorators:
            dec.update(ticks)

        #remove objects
        for obj in list(self.objects):
            if obj.should_remove():
                self.space.remove(obj.body,obj.shape)
                self.objects.remove(obj)

        #remove decorators
        for dec in list(self.decorators):
            if dec.should_remove():
                self.decorators.remove(dec)
        
        self.report_timer+=ticks
        if self.report_timer>self.report_interval:            
            print("angular velacity: ",self.my_ship.body.angular_velocity)
            print("fps: ",self.clock.get_fps())
            self.report_timer=0

    def draw(self,screen):
        self.width,self.height=screen.get_size()
        camera=Camera(screen)
        screen.fill((0,0,0))
                            
        for obj in self.objects:
            obj.get_sprite().blit(screen,camera)  
        for obj in self.decorators: 
            obj.get_sprite().blit(screen,camera)              
        
        
    def handle_event(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:    
                #self.my_ship.thruster.set_throttle(1)            
                self.my_ship.maneuver_thruster.set_throttle_ns(1)
                #self.thrust=Vec2d(0,1e5)
            if event.key == pygame.K_DOWN:
                #self.thrust=Vec2d(0,-1e5)              
                self.my_ship.maneuver_thruster.set_throttle_ns(-1)
            if event.key == pygame.K_LEFT:
                #self.my_ship.reaction_wheel.set_throttle(1)                
                self.my_ship.maneuver_thruster.set_throttle_ew(1)
            if event.key == pygame.K_RIGHT:
                self.my_ship.maneuver_thruster.set_throttle_ew(-1)
                #self.my_ship.reaction_wheel.set_throttle(-1)                                
            if event.key == pygame.K_SPACE:
                self.my_ship.fire_cannon(self)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                #self.my_ship.thruster.set_throttle(0)
                self.my_ship.maneuver_thruster.set_throttle_ns(0)

                #self.thrust=Vec2d(0,0)                
            if event.key == pygame.K_DOWN:
                self.my_ship.maneuver_thruster.set_throttle_ns(0)

                 
                ...
            if event.key == pygame.K_LEFT:
                self.my_ship.reaction_wheel.set_throttle(0)     
                self.my_ship.maneuver_thruster.set_throttle_ew(0)                           
                ...                     
            if event.key == pygame.K_RIGHT:
                self.my_ship.reaction_wheel.set_throttle(0)      
                self.my_ship.maneuver_thruster.set_throttle_ew(0)          
                ...          
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:
                pos=pygame.mouse.get_pos()
                #print("mouse pos: ",pos)
                pos=Vec2d(pos[0],-pos[1])
                arrow=pos-Vec2d(self.width,-self.height)/2                
                arrow=arrow.normalized()
                self.desired_velocity=arrow*2
                self.my_ship.set_desired_velocity(self.desired_velocity)


            if event.button==3:
                ...
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button==1:
                self.desired_velocity=Vec2d(0,0)