import pygame
from sprites.Sprite import *
from engine.GameObjects import *
from engine.Ship import *
from engine.MagnetileShip import *
import pymunk
from sprites.Background import *
from engine.Magnetile import *
from behavior_tree.NPC_control import *
from engine.HUD import *
from behavior_tree.ComplexBehaviors import *

class GameEngine:
    def __init__(self):
        self.controller=None
        #display stuff
        self.camera=Camera()
        self.min_camera_zoom=0.25
        self.max_camera_zoom=0.5
        self.camera.zoom=0.5        
        #self.default_zoom=1.0
        self.hud=HUD()
        self.hud.camera=self.camera

#        self.clock=clock
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0.0, 0.0)

        ship_bullet_collision_handler=self.space.add_collision_handler(COLLISION_TYPE_SHIP, COLLISION_TYPE_BULLET)
        ship_bullet_collision_handler.post_solve=self.bullet_hit
        ship_ship_collision_handler=self.space.add_collision_handler(COLLISION_TYPE_SHIP, COLLISION_TYPE_SHIP)
        ship_ship_collision_handler.post_solve=self.ship_collision
        ship_collectable_collision_handler=self.space.add_collision_handler(COLLISION_TYPE_SHIP, COLLISION_TYPE_COLLECTABLE)
        ship_collectable_collision_handler.post_solve=self.ship_collects

        self.objects_to_add=[]        
        self.objects =[]
        self.id_object_map={} #maps body.id to object
        self.decorators =[]
        self.background=Background()
        ...
        self.report_timer=0
        self.report_interval=5000
        
        ...

        self.my_ship=None
        #self.my_ship=get_ship_factory().get_ship("ship3")        
        #self.schedule_add_object(self.my_ship)
        #self.my_ship.thruster.sound_on=True


        #torpedo=Torpedo(position=Vec2d(-200,0),velocity=Vec2d(0,0))
        #torpedo.behavior_tree=TorpedoBehavior(npc=torpedo,engine=self)
        #torpedo.behavior_tree=InterceptShip(npc=torpedo,ship=self.my_ship)
        #self.schedule_add_object(torpedo)
        self.other_ship=None
        self.new_enemy_countdown=5000000
        self.respawn_player_countdown=5000

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
        #self.desired_velocity=Vec2d(0,0)
        #self.add_decorator(SpriteDecorator())
        self.add_decorator(Planet())
        #for i in range(5):
        #    self.spawn_asteroid()
        for i in range(1):
            self.spawn_collectable()


    def set_controller(self,controller):
        self.controller=controller
        self.hud.set_controller(controller)

    def spawn_player(self,ship_name):
        self.my_ship=get_ship_factory().get_ship(ship_name)   
        self.my_ship.is_player=True     
        #self.schedule_add_object(self.my_ship)        
        self.add_decorator(ShipSpawnDecorator(position=Vec2d(0,0),ship=self.my_ship))


    def respawn_enemy(self):
        #enemy_choices=["ship1","ship2","ship3","ship4","ship5","ship6","ship7","battleship_cruiser"]
        enemy_choices=["ship1","ship2","ship3","ship4","ship5"]
        self.other_ship=get_ship_factory().get_ship(random.choice(enemy_choices))
        offset=Vec2d(random.randrange(-1000,1000),random.randrange(-1000,1000))
        self.other_ship.body.position=Vec2d(0,800)+offset
        self.schedule_add_object(self.other_ship)
        #behavior=ParallelBehavior()
        #behavior.add_child(WanderRandomly(npc=self.other_ship,timescale=10*60) )   
        self.other_ship.behavior_tree=AggressiveBehavior(npc=self.other_ship,engine=self)        

    def spawn_asteroid(self):
        offset=Vec2d(random.randrange(-1000,1000),random.randrange(-1000,1000))
        velocity=Vec2d(random.randrange(-100,100),random.randrange(-100,100))

        asteroid=Asteroid(offset,velocity,256)
        self.schedule_add_object(asteroid)

    def spawn_collectable(self):
        offset=Vec2d(random.randrange(-1000,1000),random.randrange(-500,500))
        velocity=Vec2d(random.randrange(-100,100),random.randrange(-20,20))
        angvel=random.randrange(-1,1)
        x=Collectable(offset,velocity,angvel)
        self.schedule_add_object(x)


       
    def schedule_add_object(self,obj,delay=0):
        self.objects_to_add.append([obj,delay])

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
        if self.my_ship is not None:
            if self.my_ship not in self.objects and self.my_ship.is_dead:
                self.my_ship=None  
        else:
            self.respawn_player_countdown-=ticks
            self.hud.message="Respawning in "+str(int(self.respawn_player_countdown/1000))+" seconds"            
            if self.respawn_player_countdown<=0:
                self.respawn_player_countdown=5000
                self.spawn_player("ship1")
                self.hud.message=None                  

        if self.other_ship is None or (self.other_ship not in self.objects and self.other_ship.is_dead):
            if True:                    
                if self.new_enemy_countdown>0:
                    self.new_enemy_countdown-=ticks
                    self.hud.message="New enemy in "+str(int(self.new_enemy_countdown/1000))+" seconds"                
                else:
                    self.respawn_enemy()
                    self.new_enemy_countdown=5000
                    self.hud.message=None
        
        self.hud.update(ticks,self.my_ship)

        #update npcs
        #for npc in self.npcs:
        #    npc.execute()                      

        #update objects
        for obj in self.objects:
            obj.update(ticks,self)    

        #add new objects
        leftovers=[]
        for obj in self.objects_to_add:
            if obj[1]<=0:
                self._add_object(obj[0]) 
            else:
                leftovers.append( [obj[0],obj[1]-1] )
        self.objects_to_add=leftovers

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
            dec.update(ticks,self)

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

        if self.my_ship is None:
            return
        
        #DEBUG TEST VIEW CONE
        #objs=self.get_objects_in_cone(self.my_ship.body.position,self.my_ship.body.angle,math.pi/4,1000,filter=None)
        #if len(objs)>0:
        #    print("my angle {}".format(self.my_ship.body.angle))
        #    print("my position {}".format(self.my_ship.body.position))
        #    print("{} objects in view cone".format(len(objs)))
        #    print("{}".format(objs[0]))

        
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
        if self.my_ship is not None:
            delta_camera=self.my_ship.body.position-self.camera.position        
        else:
            delta_camera=Vec2d(0,0)-self.camera.position
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

        for obj in self.decorators: 
            if not obj.top_layer:
                obj.get_sprite().blit(screen,self.camera)                       
        for obj in self.objects:
            obj.get_sprite().blit(screen,self.camera)  
        for obj in self.decorators: 
            if obj.top_layer:
                obj.get_sprite().blit(screen,self.camera)   
        #if self.my_ship is not None: 
        self.hud.draw(self.camera,screen,self,self.my_ship)          
        
        
    def handle_event(self,event):
        self.hud.handle_event(event,self.my_ship)              

    def bullet_hit(self,arbiter,space,data):
        print("bullet hit body id is",arbiter.shapes[0].body.id)
        ship=self.id_object_map[arbiter.shapes[0].body.id]
        bullet=self.id_object_map[arbiter.shapes[1].body.id] 
        #TODO check if ship still exists        
        if not isinstance(ship,ControllableShip):
            return True
        damage=4
        if bullet.hit_this_frame:
            return True
        ship.do_damage(damage)        
        if ship.get_shields()[0]<=0:
            bullet.flag_remove()
            spray=ParticleSprayDecorator(position=bullet.body.position,velocity=ship.body.velocity)
            self.add_decorator(spray)
        bullet.hit_this_frame=True        
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

    def ship_collects(self,arbiter,space,data):
        
        ship1=self.id_object_map[arbiter.shapes[0].body.id]
        if not isinstance(ship1,MagnetileShip):
            return True
        collected=self.id_object_map[arbiter.shapes[1].body.id] 
        collected.remove_flag=True
        ship1.cargo_count+=1
        if ship1.cargo_count>=2:
            ship1.get_active_weapon(None).ammo_count+=1
            ship1.cargo_count-=2
        return True




    def point_query(self,point,max_distance,filter=None):
        #TODO Implement filter correctly
        if filter is None:
            filter=pymunk.ShapeFilter()
        bodies=self.space.point_query(point,max_distance,filter)
        ret=[]
        for b in bodies:
            object=self.id_object_map[b.shape.body.id]
            if object not in ret:
                ret.append(object)
        return ret
    
    #helper functions
    def get_objects_in_cone(self,position,angle,angle_range,max_distance,filter=None):
        objects=self.point_query(position,max_distance,filter)
        objects_in_view_cone=[]
        for object in objects:
            dx=object.body.position-position
            angle_to_object=dx.angle-math.pi/2
            delta_angle=angle_subtract(angle_to_object,angle)
            if abs(delta_angle)<angle_range and object!=self.my_ship:
                objects_in_view_cone.append(object)        
        return objects_in_view_cone