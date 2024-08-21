import pygame
import math
from mechanics.Vector2D import Vector2D

#this describes the relationship between the world and the screen
class Camera:
    def __init__(self,screen):
        self.position=Vector2D(0,0) #camera center in world coordinates
        self.screen_center=Vector2D(screen.get_width()/2,screen.get_height()/2)
        self.zoom=1

    def get_screen_position(self,world_position):
        x=(world_position-self.position)*self.zoom+self.screen_center
        return (int(x[0]),int(x[1]))


class DrawableSprite:
    def __init__(self,world_position=Vector2D(0,0)):
        self.world_position=world_position

    def set_world_position(self,position):
        self.world_position=position        

    def blit(self,screen,camera):
        ...
    

class CircleSprite(DrawableSprite):
    def __init__(self,radius=10,color=(255,255,255),world_position=Vector2D(0,0)):
        DrawableSprite.__init__(self,world_position)        
        self.radius=radius #in game units
        self.color=color

    def set_radius(self,radius):
        self.radius=radius
    
    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        pygame.draw.circle(screen,self.color,pos,self.radius*camera.zoom)        
        #side=int(math.ceil(max(self.radius,1)))*2
        #surf=pygame.Surface((side,side),flags=pygame.SRCALPHA)
        #surf.set_colorkey((0,0,0))
        #surf.fill((0,0,0))
        #pygame.draw.circle(surf,self.color,(self.radius,self.radius),self.radius)
        #return surf
    
class CompositeSprite(DrawableSprite):
    def __init__(self):
        DrawableSprite.__init__(self)
        self.sprites=[]
        self.rect=[0,0,0,0]
    
    def add_sprite(self,sprite):
        self.sprites.append(sprite)

    def blit(self,screen,camera):
        for i in range(len(self.sprites)):            
            self.sprites[i].blit(screen,camera)    