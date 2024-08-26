import pygame
from engine.GameEngine import GameEngine
from sprites.SpriteSheet import get_sprite_store
from sprites.Sprite_To_Geometry import get_geometry_store



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
engine=GameEngine(clock)
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