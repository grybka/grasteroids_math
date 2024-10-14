from pymunk import Vec2d
from sprites.SpriteSheet import get_sprite_store
from sprites.Sprite import ImageSprite
from engine.Ship import *
from behavior_tree.NPC_control import *
from behavior_tree.BehaviorTree import *

#this deals with
# taking the input and communicating it to the objects in the engin
# drawing the extra information on top of the game map

class HUD:
    def __init__(self):
        self.crosshairs_distance_px=150
        self.indicator_length_px=10
        self.camera=None
        ...
        self.loaded=False      
        self.controller=None  

        self.move_target=None

    def load_assets(self):
        self.crosshairs_image=get_sprite_store().get_sprite("crosshairs1",scale=1.0)
        self.move_target_image=get_sprite_store().get_sprite("crosshairs2",scale=1.0)

    def set_controller(self,controller):
        self.controller=controller


    def update(self,ticks,ship):
        if self.controller is not None and ship is not None:
            self.update_controller_input(ticks,ship)

    def update_controller_input(self,ticks,ship):        
        self.my_ship=ship
        axis_dead_zone=0.15
        #right stick controls direction
        axis2=self.controller.get_axis(0)  
        axis3=self.controller.get_axis(1)  
        #legt stick controls thrust
        axis0=self.controller.get_axis(2)
        axis1=self.controller.get_axis(3)
        if abs(axis0)>axis_dead_zone or abs(axis1)>axis_dead_zone:            
            arrow=Vec2d(axis0,-axis1).normalized()
            self.my_ship.set_desired_direction(arrow)
            self.my_ship.set_pointing_navigation_mode(PointingNavigationMode.SET_DIRECTION)
        else:
            self.my_ship.set_pointing_navigation_mode(PointingNavigationMode.ZERO_ANGULAR_VELOCITY)

        

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
        axis4=self.controller.get_axis(4)
        if axis4>0:
            self.my_ship.missile_launcher.firing=True
        else:
            self.my_ship.missile_launcher.firing=False      

    def handle_event(self,event,ship):
        if ship is None:
            return
        if event.type == pygame.KEYDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:
                pos=pygame.mouse.get_pos()
                target=self.camera.get_world_position(pos)
                #ship.behavior_tree=MoveToPoint(ship,target)
                ship.behavior_tree=ParallelBehavior([DoOnce(TurnTowardsPoint(ship,target)),MoveToPoint(ship,target)])
                self.move_target=target
                pass

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button==1:
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
        #Draw move target
        if self.move_target is not None:
            self.move_target_sprite=ImageSprite(self.move_target_image,self.move_target)
            self.move_target_sprite.blit(screen,camera)
        #draw indicators for offscreen ships
        for object in engine.objects: 
            if isinstance(object,ControllableShip):
                screen_pos=camera.get_screen_position(object.body.position)
                if screen_pos[0]<0 or screen_pos[0]>screen.get_width() or screen_pos[1]<0 or screen_pos[1]>screen.get_height():
                    center=( screen.get_width()/2,screen.get_height()/2)
                    screen_rect=pygame.Rect(0,0,screen.get_width(),screen.get_height())
                    new_center,indicator_pos=screen_rect.clipline(center,screen_pos)                
                    pygame.draw.circle(screen,(255,0,0),indicator_pos,10,2)
                
        