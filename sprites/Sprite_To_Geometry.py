import pygame
import pymunk
from pymunk import Vec2d
import math
import yaml

class SpriteGeometryInfo:
    def __init__(self):
        ...

    def load_geometry_info(self,filename):
        with open(filename, 'r') as file:
            self.sprite_info_file = yaml.safe_load(file)

    def get_geometry(self,sprite_name,mass=1,scale=1):        
        if sprite_name not in self.sprite_info_file:
            raise Exception("Sprite not found: "+sprite_name)
        if self.sprite_info_file[sprite_name]["type"]=="circle":
            radius=self.sprite_info_file[sprite_name]["radius"]*scale
            body=pymunk.Body(mass,pymunk.moment_for_circle(mass,0,radius,(0,0)))          
            shape=pymunk.Circle(body,radius,(0,0))
            return body,shape
        elif self.sprite_info_file[sprite_name]["type"]=="square":
            radius=self.sprite_info_file[sprite_name]["radius"]*scale
            body=pymunk.Body(mass,pymunk.moment_for_box(mass,2*radius,2*radius))          
            shape=pymunk.Poly.create_box(body,(2*radius,2*radius))
            return body,shape            
            
_geometry_store=SpriteGeometryInfo()

def get_geometry_store():
    return _geometry_store


#assume my sprite is centered
#goodness = number of pixels outside sphere - number of clearspots inside sphere
def circle_sprite_goodness(image,radius):    
    goodness=0
    circle_center=Vec2d(image.get_width()/2,image.get_height()/2)
    for x in range(image.get_width()):
        for y in range(image.get_height()):            
            pos=Vec2d(x,y)-circle_center
            if pos.length>radius:
                #outside circle
                ...                
            else:                
                if image.get_at((x,y))[3]>128:
                    goodness+=1
                else:
                    goodness-=1
    return goodness

def square_sprite_goodness(image,radius):
    goodness=0
    square_center=Vec2d(image.get_width()/2,image.get_height()/2)
    for x in range(image.get_width()):
        for y in range(image.get_height()):            
            pos=Vec2d(x,y)-square_center
            if pos.x>radius or pos.y>radius or pos.x<-radius or pos.y<-radius:
                #outside square
                ...                
            else:                
                if image.get_at((x,y))[3]>128:
                    goodness+=1
                else:
                    goodness-=1
    return goodness


#figure out the radius of the sphere that would contain the sprite
def sprite_to_circle(image):
    max_radius=int(max(image.get_width(),image.get_height())/2)
    min_radius=int(0.1*max_radius)
    best_radius=0
    best_goodness=0
    for radius in range(min_radius,max_radius):
        goodness=circle_sprite_goodness(image,radius)   
        #print(radius,goodness)     
        if goodness>best_goodness:
            best_goodness=goodness
            best_radius=radius
    return best_radius,best_goodness

    
    
def sprite_to_square(image):    
    max_radius=int(max(image.get_width(),image.get_height())/2)
    min_radius=int(0.25*max_radius)
    min_radius=1
    best_radius=0
    best_goodness=0
    for radius in range(min_radius,max_radius):
        goodness=square_sprite_goodness(image,radius)        
        if goodness>best_goodness:
            best_goodness=goodness
            best_radius=radius
    return best_radius,best_goodness