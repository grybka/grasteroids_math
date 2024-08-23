import pygame
from engine.GameEngine import GameEngine



pygame.init()
pygame.font.init()

clock=pygame.time.Clock()
engine=GameEngine(clock)


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



#loop through game engine
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