from pymunk import Vec2d
from sprites.SpriteSheet import get_sprite_store
from sprites.Sprite import ImageSprite
from engine.Ship import *
#this deals with
# taking the input and communicating it to the objects in the engin
# drawing the extra information on top of the game map

class HUD:
    def __init__(self):
        self.crosshairs_distance_px=150
        self.indicator_length_px=10
        ...
        self.loaded=False        

    def load_assets(self):
        self.crosshairs_image=get_sprite_store().get_sprite("crosshairs1",scale=1.0)

    def set_controller(self,controller):
        self.controller=controller

    def update(self,ticks,ship):
        self.my_ship=ship
        axis_dead_zone=0.15
        #left stick controls direction
        axis0=self.controller.get_axis(0)  
        axis1=self.controller.get_axis(1)  
        if abs(axis0)>axis_dead_zone or abs(axis1)>axis_dead_zone:            
            arrow=Vec2d(axis0,-axis1).normalized()
            self.my_ship.set_desired_direction(arrow)
            self.my_ship.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)
        else:
            self.my_ship.set_pointing_navigation_mode(PointingNavigationMode.ZERO_ANGULAR_VELOCITY)

        #right stick controls thrust
        axis2=self.controller.get_axis(2)
        axis3=self.controller.get_axis(3)

        if abs(axis2)>axis_dead_zone or abs(axis3)>axis_dead_zone:     
            arrow=Vec2d(axis2,-axis3)                  
            #self.my_ship.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)            
            #self.my_ship.set_desired_velocity(arrow*ship.max_speed)
            self.my_ship.set_velocity_navigation_mode(VelocityNavigationMode.SET_THRUST)
            self.my_ship.desired_thrust=arrow
        else:
            self.my_ship.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)            
            self.my_ship.set_desired_velocity(Vec2d(0,0))
            


        #right trigger controls firing
        axis5=self.controller.get_axis(5)
        
        if axis5>0:       
            self.my_ship.cannon.firing=True
        else:   
            self.my_ship.cannon.firing=False      

    def handle_event(self,event,ship):
        pass

    def draw(self,camera,screen,engine,ship):
        if not self.loaded:
            self.load_assets()
            self.loaded=True
        #Draw crosshairs
        crosshairs_distance=self.crosshairs_distance_px/camera.zoom
        pointing_vector=Vec2d(0,1).rotated(ship.body.angle)
        self.crosshairs_sprite=ImageSprite(self.crosshairs_image,ship.body.position+crosshairs_distance*pointing_vector)
        self.crosshairs_sprite.blit(screen,camera)
        #Draw desired angle
        indicator_length=self.indicator_length_px/camera.zoom
        indicator_start=ship.desired_direction*(crosshairs_distance-0.5*indicator_length)+ship.body.position
        indicator_stop=ship.desired_direction*(crosshairs_distance+0.5*indicator_length)+ship.body.position
        pygame.draw.line(screen,(255,255,255),camera.get_screen_position(indicator_start),camera.get_screen_position(indicator_stop),2)

        