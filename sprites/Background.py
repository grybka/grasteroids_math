import pygame
import random

#generate a list of random points for stars
#hash them so they're only drawn within the camera fov

class BackgroundTile:
    def __init__(self,position,width,height):
        n_stars=100
        self.stars=[]
        for i in range(n_stars):
            x=position[0]+random.randint(0,width)
            y=position[1]+random.randint(0,height)
            self.stars.append((x,y))

    def draw(self,screen,camera):
        for star in self.stars:
            screen_pos=camera.get_screen_position(star)
            if screen_pos[0]>=0 and screen_pos[0]<=screen.get_width() and screen_pos[1]>=0 and screen_pos[1]<=screen.get_height():
                pygame.draw.circle(screen,(255,255,255),screen_pos,1)

class Background:
    def __init__(self):
        self.tiles={}
        self.tile_width=1000
        self.tile_height=1000

    def draw(self,screen,camera):
        corner1=camera.get_world_position((0,0))
        corner2=camera.get_world_position((screen.get_width(),screen.get_height()))
        xmin=min(corner1[0],corner2[0])
        xmax=max(corner1[0],corner2[0])
        ymin=min(corner1[1],corner2[1])
        ymax=max(corner1[1],corner2[1])

        for x in range(int(xmin//self.tile_width),int(xmax//self.tile_width)+1):
            for y in range(int(ymin//self.tile_height),int(ymax//self.tile_height)+1):
                if (x,y) not in self.tiles:
                    self.tiles[(x,y)]=BackgroundTile((x*self.tile_width,y*self.tile_height),self.tile_width,self.tile_height)
                self.tiles[(x,y)].draw(screen,camera)
        
        
    def update(self,ticks,engine):
        pass

    def should_remove(self):
        return False