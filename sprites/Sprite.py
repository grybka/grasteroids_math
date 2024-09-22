import pygame
import math
from pymunk import Vec2d
from sprites.SpriteSheet import get_sprite_store

#this describes the relationship between the world and the screen
class Camera:
    def __init__(self):
        #self.height=screen.get_height()
        self.position=Vec2d(0,0) #camera center in world coordinates
        #self.screen_center=Vec2d(screen.get_width()/2,screen.get_height()/2)
        self.zoom=1

    def set_screen(self,screen):
        self.height=screen.get_height()
        self.width=screen.get_width()
        self.screen_center=Vec2d(screen.get_width()/2,screen.get_height()/2)

    def flipy(self,vec):
        """Small hack to convert chipmunk physics to pygame coordinates"""        
        #return -y + self.height
        return ( round(vec.x), round(-vec.y + self.height))
    
    def unflipy(self,vec):
        return Vec2d(vec[0],self.height-vec[1])
    
    


    def get_screen_position(self,world_position):        
        x=(world_position-self.position)*self.zoom+self.screen_center         
        return self.flipy(x)
        #return (round(x[0]),round(self.flipy(x[1])))
    
    def get_world_position(self,screen_position):
        pos=self.unflipy(screen_position)       
        return (pos-self.screen_center)/self.zoom+self.position
        
        


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

def clamp(x,minimum,maximum):
    return max(minimum,min(x,maximum))

def color_blend(color,delta):
    return (clamp(color[0]+delta,0,255),clamp(color[1]+delta,0,255),clamp(color[2]+delta,0,255))


class MagnetileSprite(DrawableSprite):
    def __init__(self,magnetile):
        DrawableSprite.__init__(self,Vec2d(0,0))        
        self.magnetile=magnetile

    def blit(self,screen,camera):        
        vertices=[camera.get_screen_position(self.magnetile.body.position+v.rotated(self.magnetile.body.angle)) for v in self.magnetile.vertices]
        pygame.draw.polygon(screen,self.magnetile.color,vertices)        
        for magnet in self.magnetile.magnets:
            inset=3
            radius=3*camera.zoom
            #position=camera.get_screen_position(self.magnetile.body.position+magnet.position.rotated(self.magnetile.body.angle))
            position=camera.get_screen_position(self.magnetile.body.position+(magnet.position-inset*magnet.normal).rotated(self.magnetile.body.angle))
            if magnet.polarity==1:
                pygame.draw.circle(screen,color_blend(self.magnetile.color,-20),position,radius)
            else:
                pygame.draw.circle(screen,color_blend(self.magnetile.color,20),position,radius)


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
        pygame.draw.circle(screen,self.color,pos,max(self.radius*camera.zoom,1))        

class ImageSprite(DrawableSprite):
    def __init__(self,image,world_position=Vec2d(0,0),angle=0):
        DrawableSprite.__init__(self,world_position)
        self.angle=angle
        self.image=image


    def set_angle(self,angle):
        self.angle=angle

    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        image=self.image
        if camera.zoom !=1:
            image=pygame.transform.scale(image,(int(image.get_width()*camera.zoom),int(image.get_height()*camera.zoom)))        
        if self.angle!=0:
            image=pygame.transform.rotate(image,math.degrees(self.angle))
        
        #rotated_image=self.image
        screen.blit(image,(pos[0]-image.get_width()/2,pos[1]-image.get_height()/2))

class AnimationSprite(DrawableSprite):
    def __init__(self,animation,world_position=Vec2d(0,0),angle=0,frame_time=0.1):
        DrawableSprite.__init__(self,world_position)
        self.angle=angle
        self.animation=animation
        self.frame=0
        self.time_since_last_frame=0
        self.frame_time=frame_time
        self.clip_rect=None        

    def set_angle(self,angle):
        self.angle=angle

    def blit(self,screen,camera):
        pos=camera.get_screen_position(self.world_position)
        image=self.animation[self.frame]
        
        if self.clip_rect is not None:
            a=self.clip_rect[0] or 0
            b=self.clip_rect[1] or 0
            c=self.clip_rect[2] or image.get_width()
            d=self.clip_rect[3] or image.get_height()
            if c>image.get_width():
                c=image.get_width()
            if d>image.get_height():
                d=image.get_height()
            my_rect=(a,b,c,d)
            #print("clipping to ",my_rect)
            image=image.subsurface(my_rect)
            

            
        if camera.zoom !=1:
            image=pygame.transform.scale(image,(int(image.get_width()*camera.zoom),int(image.get_height()*camera.zoom)))        
        if self.angle!=0:
            image=pygame.transform.rotate(image,math.degrees(self.angle))
                
        screen.blit(image,(pos[0]-image.get_width()/2,pos[1]-image.get_height()/2))

    def update(self,ticks):
        self.time_since_last_frame+=ticks/1000
        if self.time_since_last_frame>self.frame_time:
            self.time_since_last_frame=self.time_since_last_frame-self.frame_time
            self.frame+=1
            if self.frame>=len(self.animation):
                self.frame=0

class CompoundSprite(DrawableSprite):
    def __init__(self,sprites=[]):
        DrawableSprite.__init__(self)
        self.sprites=sprites

    def add_sprite(self,sprite):
        self.sprites.append(sprite)

    def blit(self,screen,camera):        
        for sprite in self.sprites:
            sprite.blit(screen,camera)

#a sprite made up of magnetiles
#where it is worth blitting them onto a single surface so it acts like an image sprite
        
class MagnetileConstructionSprite:
    def __init__(self,construction):
        self.construction=construction
        self.image=None

    def build_image(self):
        print("building image")
        bbox=self.construction.get_bbox()
        #because of the way the sprite is built, this needs to be centered rectangle even though the bbox is not
        # center of mass issues
        xradius=max(abs(bbox[0]),abs(bbox[2]))
        yradius=max(abs(bbox[1]),abs(bbox[3]))        
        
        self.image=pygame.Surface( (math.ceil(2*xradius),math.ceil(2*yradius)),pygame.SRCALPHA)
        empty_camera=Camera()
        empty_camera.set_screen(self.image)
        for magnetile in self.construction.magnetiles:
            sprite=MagnetileSprite(magnetile)
            sprite.blit(self.image,empty_camera)
        print("image width height ",self.image.get_width(),self.image.get_height())
        
    def blit(self,screen,camera):
        if self.image is None:
            self.build_image()
        image=self.image
        angle=self.construction.body.angle
        pos=camera.get_screen_position(self.construction.body.position)        
        if camera.zoom !=1:
            image=pygame.transform.scale(image,(int(image.get_width()*camera.zoom),int(image.get_height()*camera.zoom)))        
        if angle!=0:
            image=pygame.transform.rotate(image,math.degrees(angle))
        
        #rotated_image=self.image
        screen.blit(image,(pos[0]-image.get_width()/2,pos[1]-image.get_height()/2))

class HealthBar(DrawableSprite):
    def __init__(self,ship):
        DrawableSprite.__init__(self)
        self.update_ship(ship)
        self.color_background=(255,255,255)
        self.color_bar_background=(0,0,0)
        self.color_shields=pygame.Color("aqua")
        self.color_health=(255,0,0)
        self.width=40
        self.bar_height=2

    def update_ship(self,ship):
        self.ship=ship

    def blit(self,screen,camera):        

        health,max_health=self.ship.get_health()
        shields,max_shields=self.ship.get_shields()
        pos=camera.get_screen_position(self.ship.body.position+Vec2d(self.ship.bbox[2],self.ship.bbox[3])+Vec2d(0,self.bar_height))
        #draw background
        pygame.draw.rect(screen,self.color_background,(pos[0]-1,pos[1]-1,self.width+2,2*self.bar_height+3))
        #draw health
        pygame.draw.rect(screen,self.color_bar_background,(pos[0],pos[1],self.width,self.bar_height))
        pygame.draw.rect(screen,self.color_health,(pos[0],pos[1],round(health*self.width/max_health),self.bar_height))        
        #draw shields
        offset=self.bar_height+1
        pygame.draw.rect(screen,self.color_bar_background,(pos[0],pos[1]+offset,self.width,self.bar_height))
        pygame.draw.rect(screen,self.color_shields,(pos[0],pos[1]+offset,round(shields*self.width/max_shields),self.bar_height))
        