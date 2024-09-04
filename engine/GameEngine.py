import pygame
from sprites.Sprite import *
from engine.GameObjects import *
from engine.Ship import *
import pymunk
from sprites.Background import *
from engine.Magnetile import *
from engine.NPC_control import *

class GameEngine:
    def __init__(self,clock):
        self.controller=None
        #display stuff
        self.camera=Camera()
        self.min_camera_zoom=0.3
        self.max_camera_zoom=1
        self.default_zoom=1

        self.clock=clock
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0.0, 0.0)

        ship_bullet_collision_handler=self.space.add_collision_handler(COLLISION_TYPE_SHIP, COLLISION_TYPE_BULLET)
        ship_bullet_collision_handler.begin=self.bullet_hit

        self.objects_to_add=[]        
        self.objects =[]
        self.id_object_map={} #maps body.id to object
        self.decorators =[]
        self.background=Background()
        ...
        self.report_timer=0
        self.report_interval=2000
        
        ...
    
        #self.my_ship=Ship()
        self.my_ship=MagnetileShip(shape_fname="tile_arrangements/ship1.yaml")
        #self.my_ship=MagnetileShip(shape_fname="tile_arrangements/ship2.yaml")
        self.schedule_add_object(self.my_ship)
        self.my_ship.thruster.sound_on=True


        self.other_ship=MagnetileShip(shape_fname="tile_arrangements/ship2.yaml")
        self.other_ship.body.position=Vec2d(0,1000)
        self.schedule_add_object(self.other_ship)
        #self.add_object(SquareMagnetile(position=Vec2d(40,1000)))
        #self.add_object(RightTriangleMagnetile(position=Vec2d(100,1000)))
        #self.add_object(EquilateralTriangleMagnetile(position=Vec2d(160,1000)))
        #self.add_object(IsocelesTriangleMagnetile(position=Vec2d(220,1000)))
        #self.add_object(TallRightTriangleMagnetile(position=Vec2d(280,1000)))
        #for i in range(5):
        #    for j in range(5):
        #        self.add_object(SquareMagnetile(position=Vec2d(40*j,1000+40*i)))
        #self.add_object(BarMagnet(position=Vec2d(0,200),length=20e4))
        #self.add_object(BarMagnet(position=Vec2d(40,240),length=20e4))
        #self.add_object(ChargedSphere(position=Vec2d(0,200),charge=1))
        #self.add_object(ChargedSphere(position=Vec2d(60,200),charge=-1))
        self.desired_velocity=Vec2d(0,0)

        self.npcs=[]
        #self.npcs.append( TurnTowardsPlayer(npc=self.other_ship,player=self.my_ship,angle_threshold=0.1) )        
        #self.npcs.append( ApproachTarget(npc=self.other_ship,target=self.my_ship,radius=10) )
        self.npcs.append( ApproachToDistance(npc=self.other_ship,player=self.my_ship,too_close=100,too_far=200) )

    def schedule_add_object(self,obj):
        self.objects_to_add.append(obj)

    def _add_object(self,obj):
        if isinstance(obj.shape,list):
            self.space.add(obj.body, *obj.shape)
        else:
            self.space.add(obj.body,obj.shape)
        self.objects.append(obj)
        self.id_object_map[obj.body.id]=obj

    def add_decorator(self,dec):
        self.decorators.append(dec)

    def update_controls(self):
        if self.controller is not None:
            self.update_controller_input()
            return
  
        #Mouse controls
        #If mouse button 1 is pressed, the ship will move towards the mouse position
        if pygame.mouse.get_pressed()[0]:
            pos=pygame.mouse.get_pos()
            world_pos=self.camera.get_world_position(pos)                
            arrow=world_pos-self.my_ship.body.position
            arrow=arrow.normalized()
            desired_velocity=arrow*1000
            self.my_ship.navigation_mode=NavigationMode.SET_VELOCITY_AND_DIRECTION
            #self.my_ship.navigation_mode=NavigationMode.SET_DIRECTION
            self.my_ship.desired_velocity=desired_velocity
            self.my_ship.desired_direciton=arrow
        else:
            self.my_ship.navigation_mode=NavigationMode.ZERO_ANGULAR_VELOCITY

    def update_controller_input(self):
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
            #arrow=Vec2d(axis2,-axis3).normalized()
            arrow=Vec2d(axis2,-axis3)
            #desired_velocity=arrow*1000
            #self.my_ship.set_desired_velocity(desired_velocity)
            #self.my_ship.set_velocity_navigation_mode(VelocityNavigationMode.SET_VELOCITY)            
            self.my_ship.set_velocity_navigation_mode(VelocityNavigationMode.SET_THRUST)
            self.my_ship.desired_thrust=arrow
        else:
            #if self.my_ship.velocity_navigation_mode==VelocityNavigationMode.SET_VELOCITY:
            if self.my_ship.velocity_navigation_mode==VelocityNavigationMode.SET_THRUST:
                self.my_ship.thrusters_off()
            self.my_ship.set_velocity_navigation_mode(VelocityNavigationMode.MANUAL)            
            


        #right trigger controls firing
        axis5=self.controller.get_axis(5)
        
        if axis5>0:       
            self.my_ship.cannon.firing=True
        else:   
            self.my_ship.cannon.firing=False                          
            

    def update(self,ticks):
        #update npcs
        for npc in self.npcs:
            npc.execute()
        #update controls
        self.update_controls()        

        #update objects
        for obj in self.objects:
            obj.update(ticks,self)    

        #add new objects
        for obj in self.objects_to_add:
            self._add_object(obj) 
        self.objects_to_add=[]

        #update interactions        
        for i in range(len(self.objects)):
            for j in range(i+1,len(self.objects)):                
                if isinstance(self.objects[i],ChargedSphere) and isinstance(self.objects[j],ChargedSphere):
                    r=self.objects[j].body.position-self.objects[i].body.position
                    f=-1e5*self.objects[i].charge*self.objects[j].charge*r.normalized()/r.get_length_sqrd()
                    self.objects[i].body.apply_force_at_world_point(f,self.objects[i].body.position)
                    self.objects[j].body.apply_force_at_world_point(-f,self.objects[j].body.position)


        #update physics        
        self.space.step(ticks/1000.0)        

        #update decorators
        for dec in self.decorators:
            dec.update(ticks)

        #remove objects
        for obj in list(self.objects):
            if obj.should_remove():
                del self.id_object_map[obj.body.id]
                if isinstance(obj.shape,list):
                    self.space.remove(obj.body, *obj.shape)
                else:
                    self.space.remove(obj.body,obj.shape)
                self.objects.remove(obj)

        #remove decorators
        for dec in list(self.decorators):
            if dec.should_remove():
                self.decorators.remove(dec)
        
        self.report_timer+=ticks
        if self.report_timer>self.report_interval:               
            print("ship position: ",self.my_ship.body.position)
            print("ship velocity: ",self.my_ship.body.velocity)
            print("ship angle: ",self.my_ship.body.angle)
            print("camera zoom: ",self.camera.zoom)
            #print("fps: ",self.clock.get_fps())
            self.report_timer=0

    def draw(self,screen):
        self.camera.set_screen(screen)
        #Do camera tracking
        delta_camera=self.my_ship.body.position-self.camera.position        
        self.camera.position+=delta_camera*0.01/self.camera.zoom
        upscale_length=100
        downscale_length=50
        if delta_camera.length>upscale_length/self.camera.zoom and self.camera.zoom>self.min_camera_zoom:
            self.camera.zoom*=0.995
        elif delta_camera.length<downscale_length/self.camera.zoom and self.camera.zoom<self.max_camera_zoom:
            self.camera.zoom*=1.005        

        self.width,self.height=screen.get_size()
        
        screen.fill((0,0,0))
        self.background.draw(screen,self.camera)
                            
        for obj in self.objects:
            obj.get_sprite().blit(screen,self.camera)  
        for obj in self.decorators: 
            obj.get_sprite().blit(screen,self.camera)              
        
        
    def handle_event(self,event):
        #print(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:    
                #self.my_ship.thruster.set_throttle(1)            
                self.my_ship.maneuver_thruster.set_throttle_ns(1)
                #self.thrust=Vec2d(0,1e5)
            if event.key == pygame.K_DOWN:
                #self.thrust=Vec2d(0,-1e5)              
                self.my_ship.maneuver_thruster.set_throttle_ns(-1)
            if event.key == pygame.K_LEFT:
                #self.my_ship.reaction_wheel.set_throttle(1)                
                self.my_ship.maneuver_thruster.set_throttle_ew(1)
            if event.key == pygame.K_RIGHT:
                self.my_ship.maneuver_thruster.set_throttle_ew(-1)
                #self.my_ship.reaction_wheel.set_throttle(-1)                                
            if event.key == pygame.K_SPACE:
                self.my_ship.cannon.firing=True            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                #self.my_ship.thruster.set_throttle(0)
                self.my_ship.maneuver_thruster.set_throttle_ns(0)

                #self.thrust=Vec2d(0,0)                
            if event.key == pygame.K_DOWN:
                self.my_ship.maneuver_thruster.set_throttle_ns(0)

                 
                ...
            if event.key == pygame.K_LEFT:
                self.my_ship.reaction_wheel.set_throttle(0)     
                self.my_ship.maneuver_thruster.set_throttle_ew(0)                           
                ...                     
            if event.key == pygame.K_RIGHT:
                self.my_ship.reaction_wheel.set_throttle(0)      
                self.my_ship.maneuver_thruster.set_throttle_ew(0)          
                ...          
            if event.key == pygame.K_SPACE:
                self.my_ship.cannon.firing=False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:                
                pos=pygame.mouse.get_pos()
                """
                world_pos=self.camera.get_world_position(pos)                

                #pos=Vec2d(pos[0],-pos[1])
                #arrow=pos-Vec2d(self.width,-self.height)/2                
                arrow=world_pos-self.my_ship.body.position
                arrow=arrow.normalized()
                desired_velocity=arrow*100
                #self.my_ship.navigation_mode=NavigationMode.SET_DIRECTION
                #self.my_ship.desired_direciton=arrow
                
                self.my_ship.navigation_mode=NavigationMode.SET_VELOCITY_AND_DIRECTION
                self.my_ship.desired_velocity=desired_velocity
                self.my_ship.desired_direciton=arrow

                #self.my_ship.set_desired_velocity(self.desired_velocity)
                """


            if event.button==3:
                ...
            if event.button==4:
                if self.default_zoom<self.max_camera_zoom:
                    self.default_zoom*=1.1
            if event.button==5:
                if self.default_zoom>self.min_camera_zoom:
                    self.default_zoom*=0.9
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button==1:
                self.desired_velocity=Vec2d(0,0)
                #self.my_ship.navigation_mode=NavigationMode.MANUAL
                self.my_ship_navigation_mode=NavigationMode.ZERO_ANGULAR_VELOCITY
                self.my_ship.thrusters_off()                

    def bullet_hit(self,arbiter,space,data):
        #print("bullet hit")
        ship=self.id_object_map[arbiter.shapes[0].body.id]
        bullet=self.id_object_map[arbiter.shapes[1].body.id]
        #print("ship type is",type(ship))
        #print("bullet type is",type(bullet))
        #if ship==self.other_ship:
        #self.other_ship.explode(self)
        self.other_ship.do_damage(1)
        bullet.flag_remove()
        spray=ParticleSprayDecorator(position=bullet.body.position,velocity=ship.body.velocity)
        self.add_decorator(spray)

        return True
        