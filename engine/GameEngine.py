import pygame
from sprites.Sprite import *
from engine.GameObjects import *
from engine.Ship import *
import pymunk
from sprites.Background import *
from engine.Magnetile import *
from engine.NPC_control import *
from engine.HUD import *

class GameEngine:
    def __init__(self,clock):
        self.controller=None
        #display stuff
        self.camera=Camera()
        self.min_camera_zoom=0.25
        self.max_camera_zoom=0.5
        self.camera.zoom=0.5        
        #self.default_zoom=1.0
        self.hud=HUD()
        self.hud.camera=self.camera

        self.clock=clock
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0.0, 0.0)

        ship_bullet_collision_handler=self.space.add_collision_handler(COLLISION_TYPE_SHIP, COLLISION_TYPE_BULLET)
        ship_bullet_collision_handler.post_solve=self.bullet_hit
        ship_ship_collision_handler=self.space.add_collision_handler(COLLISION_TYPE_SHIP, COLLISION_TYPE_SHIP)
        ship_ship_collision_handler.post_solve=self.ship_collision

        self.objects_to_add=[]        
        self.objects =[]
        self.id_object_map={} #maps body.id to object
        self.decorators =[]
        self.background=Background()
        ...
        self.report_timer=0
        self.report_interval=5000
        
        ...

        self.my_ship=get_ship_factory().get_ship("ship3")        
        self.schedule_add_object(self.my_ship)
        self.my_ship.thruster.sound_on=True


        torpedo=Torpedo(position=Vec2d(-200,0),velocity=Vec2d(0,0))
        torpedo.behavior_tree=InterceptShip(npc=torpedo,ship=self.my_ship)
        self.schedule_add_object(torpedo)
        self.other_ship=None
        #self.respawn_enemy()
        #self.other_ship=get_ship_factory().get_ship("ship2")        
        #self.other_ship.body.position=Vec2d(0,800)        
        #self.schedule_add_object(self.other_ship)
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

        #self.npcs=[]
        #self.npcs.append( TurnTowardsPlayer(npc=self.other_ship,player=self.my_ship,angle_threshold=0.1) )        
        #self.npcs.append( ApproachTarget(npc=self.other_ship,target=self.my_ship,radius=10) )
        #self.npcs.append( ApproachToDistance(npc=self.other_ship,player=self.my_ship,too_close=100,too_far=200) )

        #approach point and then hold position
        #behavior=SequenceBehavior()
        #behavior=ParallelBehavior()
        #behavior.add_child(WanderRandomly(npc=self.other_ship,arena_size=(2000,2000),timescale=10*60) )
        #behavior.add_child(MoveToPoint(npc=self.other_ship,point=Vec2d(200,800),point_threshold=10) )
        #behavior.add_child(TurnTowardsPlayer(npc=self.other_ship,player=self.my_ship) )
        #behavior.add_child(FireAtPlayer(npc=self.other_ship,player=self.my_ship) )
        #self.npcs.append( behavior )
        #self.npcs.append( MoveToPoint(npc=self.other_ship,point=Vec2d(200,800),point_threshold=5) )

    def set_controller(self,controller):
        self.controller=controller
        self.hud.set_controller(controller)

    def respawn(self):
        self.my_ship=get_ship_factory().get_ship("ship5")        
        self.schedule_add_object(self.my_ship)

    def respawn_enemy(self):
        enemy_choices=["ship1","ship2","ship3","ship4","ship5","ship6","ship7"]
        self.other_ship=get_ship_factory().get_ship(random.choice(enemy_choices))
        self.other_ship.body.position=Vec2d(0,800)        
        self.schedule_add_object(self.other_ship)
        behavior=ParallelBehavior()
        behavior.add_child(WanderRandomly(npc=self.other_ship,timescale=10*60) )
        self.other_ship.behavior_tree=behavior        

       
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

    def update(self,ticks):
        if self.my_ship not in self.objects and self.my_ship.is_dead:
            self.respawn()

        if self.other_ship is None or (self.other_ship not in self.objects and self.other_ship.is_dead):
            ...
            self.respawn_enemy()

        self.hud.update(ticks,self.my_ship)

        #update npcs
        #for npc in self.npcs:
        #    npc.execute()                      

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
        dead_length=10
        if ( delta_camera.length-dead_length>upscale_length/self.camera.zoom and self.camera.zoom>self.min_camera_zoom ) or self.camera.zoom>self.max_camera_zoom:
            self.camera.zoom*=0.995
            if self.camera.zoom<self.min_camera_zoom:
                self.camera.zoom=self.min_camera_zoom
        elif ( delta_camera.length+dead_length<downscale_length/self.camera.zoom and self.camera.zoom<self.max_camera_zoom ) or self.camera.zoom<self.min_camera_zoom:
            self.camera.zoom*=1.005        
            if self.camera.zoom>self.max_camera_zoom:
                self.camera.zoom=self.max_camera_zoom

        self.width,self.height=screen.get_size()
        
        screen.fill((0,0,0))
        self.background.draw(screen,self.camera)
                            
        for obj in self.objects:
            obj.get_sprite().blit(screen,self.camera)  
        for obj in self.decorators: 
            obj.get_sprite().blit(screen,self.camera)    
        self.hud.draw(self.camera,screen,self,self.my_ship)          
        
        
    def handle_event(self,event):
        self.hud.handle_event(event,self.my_ship)              

    def bullet_hit(self,arbiter,space,data):
        #print("bullet hit")
        ship=self.id_object_map[arbiter.shapes[0].body.id]
        bullet=self.id_object_map[arbiter.shapes[1].body.id] 
        #TODO check if ship still exists        
        if not isinstance(ship,ControllableShip):
            return True
        damage=6
        ship.do_damage(damage)        
        bullet.flag_remove()
        spray=ParticleSprayDecorator(position=bullet.body.position,velocity=ship.body.velocity)
        self.add_decorator(spray)
        return True
        
    def ship_collision(self,arbiter,space,data):
        ship1=self.id_object_map[arbiter.shapes[0].body.id]
        ship2=self.id_object_map[arbiter.shapes[1].body.id] 
        total_ke=arbiter.total_ke
        ke_to_damage_coversion=1e7
        damage=total_ke/ke_to_damage_coversion
        if isinstance(ship1,ControllableShip):
            ship1.do_damage(damage)
        if isinstance(ship2,ControllableShip):
            ship2.do_damage(damage)
        return True

        #print("collision ke is",total_ke)

    def point_query(self,point,max_distance,filter=None):
        if filter is None:
            filter=pymunk.ShapeFilter()
        bodies=self.space.point_query(point,max_distance,filter)
        ret=[]
        for b in bodies:
            object=self.id_object_map[b.shape.body.id]
            if object not in ret:
                ret.append(object)
        return ret