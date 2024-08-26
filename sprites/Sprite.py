import pygame
import math
from pymunk import Vec2d
from sprites.SpriteSheet import get_sprite_store

#this describes the relationship between the world and the screen
class Camera:
    def __init__(self,screen):
        self.height=screen.get_height()
        self.position=Vec2d(0,0) #camera center in world coordinates
        self.screen_center=Vec2d(screen.get_width()/2,screen.get_height()/2)
        self.zoom=1

    def flipy(self,y):
        """Small hack to convert chipmunk physics to pygame coordinates"""        
        return -y + self.height


    def get_screen_position(self,world_position):        
        x=(world_position-self.position)*self.zoom+self.screen_center         
        return (round(x[0]),round(self.flipy(x[1])))


class DrawableSprite:
    def __init__(self,world_position=Vec2d(0,0)):
        self.world_position=world_position

    def set_world_position(self,position):
        self.world_position=position        

    def blit(self,screen,camera):
        ...
    
class DebugPolySprite(DrawableSprite):
    def __init__(self,vertices=[],color=(255,255,255),world_position=Vec2d(0,0),angle=0):
        DrawableSprite.__init__(self,world_position)        
        self.vertices=vertices #in game units
        self.color=color
        self.angle=angle

    def set_vertices(self,vertices):
        self.vertices=vertices
    
    def blit(self,screen,camera):        
        vertices=[camera.get_screen_position(self.world_position+v.rotated(self.angle)) for v in self.vertices]
        pygame.draw.polygon(screen,self.color,vertices)

class CircleSprite(DrawableSprite):
    def __init__(self,radius=10,color=(255,255,255),world_position=Vec2d(0,0)):
        DrawableSprite.__init__(self,world_position)        
        self.radius=radius #in game units
        self.color=color

    def set_radius(self,radius):
        self.radius=radius

    def set_angle(self,angle):
        ...
    
    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        pygame.draw.circle(screen,self.color,pos,self.radius*camera.zoom)        

class ImageSprite(DrawableSprite):
    def __init__(self,image,world_position=Vec2d(0,0),angle=0):
        DrawableSprite.__init__(self,world_position)
        self.angle=angle
        self.image=image


    def set_angle(self,angle):
        self.angle=angle

    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        rotated_image=pygame.transform.rotate(self.image,math.degrees(self.angle))
        #rotated_image=self.image
        screen.blit(rotated_image,(pos[0]-rotated_image.get_width()/2,pos[1]-rotated_image.get_height()/2))

class CompoundSprite(DrawableSprite):
    def __init__(self,sprites=[]):
        DrawableSprite.__init__(self)
        self.sprites=sprites

    def add_sprite(self,sprite):
        self.sprites.append(sprite)

    def blit(self,screen,camera):        
        for sprite in self.sprites:
            sprite.blit(screen,camera)