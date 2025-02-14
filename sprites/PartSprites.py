from sprites.Sprite import DrawableSprite, ViewConeSprite
from pymunk.vec2d import Vec2d
import math
import pygame


class TurretSprite(DrawableSprite):
    def __init__(self, turret):
        super().__init__()
        self.ship_angle=0
        #self.turret_angle = turret.angle
        self.color=(100,100,100)
        self.radius=10
        if turret is not None:
            self.update_from_turret(turret)
        else:
            self.min_angle=-math.pi/4
            self.max_angle=math.pi/4
            self.world_angle=0

    def update_from_turret(self,turret):
        #self.turret=turret
        self.min_angle=turret.min_angle
        self.max_angle=turret.max_angle
        self.world_angle=turret.get_world_angle()

    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        pygame.draw.circle(screen,self.color,pos,max(self.radius*camera.zoom,1))   
        #Draw pointing 
        dir=Vec2d(0,1).rotated(self.world_angle)
        target=camera.get_screen_position(self.world_position+dir*self.radius)
        pygame.draw.line(screen,(250,250,250),pos,target)



        angle=0.5*(self.min_angle+self.max_angle)+self.ship_angle
        arange=0.5*(self.max_angle-self.min_angle)
        #print("TurretSprite.blit: angle=%f, arange=%f" % (angle, arange))

        #view_cone=ViewConeSprite(self.world_position,angle,arange,20)
        #view_cone.blit(screen,camera)
        