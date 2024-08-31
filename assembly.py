import sys
import pygame
from engine.AssemblyLayer import *
from sprites.SpriteSheet import get_sprite_store
from sprites.Sprite_To_Geometry import get_geometry_store
from engine.Magnetile import *

filename=None
if len(sys.argv)>1:
    filename=sys.argv[1]

pygame.init()
pygame.font.init()

clock=pygame.time.Clock()


#set up the window to draw
displayinfo=pygame.display.Info()
max_x=2*1024
max_y=2*768
if displayinfo.current_w*0.9<max_x:
    max_x=int(displayinfo.current_w*0.9)
if displayinfo.current_h*0.8<max_y:
    max_y=int(displayinfo.current_h*0.8)
resolution=(max_x,max_y)
screen=pygame.display.set_mode(resolution)


#set up the sprite store
get_sprite_store().load_sheet_info("config/sprites.yaml")
#set up the geometry store
get_geometry_store().load_geometry_info("config/sprite_geometry.yaml")



#loop through game engine
        
engine=AssemblyLayer(clock)

if filename is not None:
    with open(filename,"r") as f:
        d=yaml.safe_load(f)
        object=MagnetileConstruction.from_dict(d)
        engine.add_to_placement_space(object)

running=True
while running:
    clock.tick(60)
    engine.update(clock.get_time())    
    
    engine.draw(screen)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                running=False
        if event.type==pygame.QUIT:
            running=False        
        engine.handle_event(event)