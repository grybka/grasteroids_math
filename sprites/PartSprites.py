from sprites.Sprite import DrawableSprite
from pymunk.vec2d import Vec2d
import pygame

class TurretSprite(DrawableSprite):
    def __init__(self, turret):
        super().__init__()
        self.ship_angle=0
        self.angle = turret.angle
        self.color=(100,100,100)
        self.radius=10
        self.min_angle=turret.min_angle
        self.max_angle=turret.max_angle

    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        pygame.draw.circle(screen,self.color,pos,max(self.radius*camera.zoom,1))    

        #Draw target cone
        center=pos
        pt1=camera.get_screen_position(self.world_position+Vec2d(1,0).rotated(self.min_angle+self.ship_angle)*self.radius*5)
        pt2=camera.get_screen_position(self.world_position+Vec2d(1,0).rotated(self.max_angle+self.ship_angle)*self.radius*5)        
        pygame.draw.polygon(screen,(200,0,0),(center,pt1,pt2))
        dir=Vec2d(1,0).rotated(-self.angle-self.ship_angle)
        pygame.draw.line(screen,(250,250,250),pos,pos+dir*camera.zoom*self.radius)