import pygame
import pymunk
from sprites.Sprite import *
from engine.MagnetileShip import *
from gui.DesignerMenus import *
from engine.Ship import ControllableShip

class PartHolderShip(ControllableShip):
    def __init__(self):
        super().__init__()
        self.body = pymunk.Body(1,1)
        self.part=None    

    def get_sprite(self):
        #sprite=ShipSprite(self)
        #for part in self.ship_parts:
        #    sprite.add_part(part)
        #return sprite
        return self.part.get_sprite(self)



class TurretDummy:
    def __init__(self):
        self.position=Vec2d(0,0)
        self.my_sprite=TurretSprite(None)

    def set_position(self,position):
        self.position=position
        self.my_sprite.world_position=position


    def get_sprite(self):
        return self.my_sprite

class ShipBuilderEngine(UIPanel):
    def __init__(self,ui_manager):
        super().__init__(ui_manager.get_root_container().get_rect(),0,ui_manager,
                         anchors={'left': 'left',
                                  'right': 'right',
                                  'top': 'top',
                                  'bottom': 'bottom'})
        game_surface_size = (ui_manager.get_root_container().get_rect().width,ui_manager.get_root_container().get_rect().height)
        self.game_surface_element = UIImage(ui_manager.get_root_container().get_rect(),
                                            pygame.Surface(game_surface_size).convert(),
                                            manager=ui_manager,
                                            container=self,
                                            parent_element=self)
        self.placement_space = pymunk.Space()
        self.placement_camera=Camera() 
        self.ui_manager=ui_manager
        enemy_choices=["ship1","ship2","ship3","ship4","ship5"]
        #self.the_ship=get_ship_factory().get_ship(random.choice(enemy_choices))
        self.the_ship=MagnetileShip()
        self.selection_window=MagnetileDesigner(self.ui_manager,self)
        #self.selection_window=MagnetileSelection(self.ui_manager,self)

        self.dragging_object=None
        self.paired_dragging_object=None
        self.part_holder_ship=PartHolderShip()
        self.placement_space.add(self.part_holder_ship.body)

        self.placement_space.step(1/1000)
        self.pair_mode=False

    def process_event(self, event):
        handled = super().process_event(event)
    #def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:         
                if self.dragging_object is not None:
                    if isinstance(self.dragging_object,Magnetile):
                        #attach the dragging object to the ship
                        self.remove_ship()
                        self.the_ship.add_magnetile(self.dragging_object)
                        if self.paired_dragging_object is not None:
                            self.the_ship.add_magnetile(self.paired_dragging_object)
                            self.paired_dragging_object=None
                        self.add_ship()
                        self.dragging_object=None
                    elif self.dragging_object==self.part_holder_ship:
                        part=self.part_holder_ship.part
                        part.attachment=self.dragging_object.body.position-self.the_ship.body.position                      
                        self.the_ship.add_part(part)                        
                        #part.debug_print()
                        if self.pair_mode:
                            part2=copy.deepcopy(part)
                            part2.attachment=Vec2d(-part.attachment[0],part.attachment[1])
                            self.the_ship.add_part(part2)
                        self.part_holder_ship.part=None                        
                        self.dragging_object=None
                        return True
                        #part.debug_print()
                    else:
                        abort("unknown dragging object",self.dragging_object)

                        ...
                else:
                    pos=pygame.mouse.get_pos()

                    #check if we clicked on a magnetile
                    world_pos=self.placement_camera.get_world_position(pos)
                    selected_part=self.the_ship.point_query_part(world_pos)
                    if selected_part is not None:
                        print("selected part is ",selected_part)
                        self.dragging_object=selected_part
                        self.the_ship.remove_part(selected_part)

                    selected_magnetile=self.the_ship.point_query(world_pos)
                    if selected_magnetile is not None:
                        self.dragging_object=selected_magnetile.my_copy()
                        self.remove_ship()
                        self.the_ship.remove_magnetile(selected_magnetile)
                        self.add_ship()
            if event.button==3: #remove object            
                self.dragging_object=None
            if event.button==4:
                if self.dragging_object is not None:
                    self.dragging_object.body.angle+=0.3
                else:
                    self.placement_camera.zoom*=0.9
                
            if event.button==5:
                if self.dragging_object is not None:
                    self.dragging_object.body.angle-=0.3
                else:
                    self.placement_camera.zoom*=1.1      

            if event.button==2:
                if self.dragging_object is not None:
                    self.dragging_object=self.dragging_object.invert() 
                    
        return False

    def update(self,ticks):
        if self.dragging_object is not None:
            pos=pygame.mouse.get_pos() 
            world_pos=self.placement_camera.get_world_position(pos)
            self.dragging_object.set_position(world_pos)
            #TODO need to think about how to represent ship first
            if isinstance(self.dragging_object,Magnetile):
                self.check_snap()          
        #self.placement_space.step(1/1000)


    def draw(self):
        screen=self.game_surface_element.image
        self.placement_camera.set_screen(screen)
        screen.fill((0,0,0))
        #draw a dashed line down the center
        dashed_line_color=(255,255,255)
        line_top=self.placement_camera.get_screen_position(Vec2d(0,400))
        line_bottom=self.placement_camera.get_screen_position(Vec2d(0,-400))
        n_dashes=20
        for i in range(n_dashes):
            if i%2==0:
                continue
            x1=int(line_bottom[0]+(line_top[0]-line_bottom[0])*i/n_dashes)
            x2=int(line_bottom[0]+(line_top[0]-line_bottom[0])*(i+1)/n_dashes)
            y1=int(line_bottom[1]+(line_top[1]-line_bottom[1])*i/n_dashes)
            y2=int(line_bottom[1]+(line_top[1]-line_bottom[1])*(i+1)/n_dashes)            
            pos1=(x1,y1)
            pos2=(x2,y2)
            pygame.draw.line(screen,dashed_line_color,pos1,pos2,1)        


        self.the_ship.get_sprite().blit(screen,self.placement_camera)
        #draw the dragging object
        if self.dragging_object is not None:
            self.dragging_object.get_sprite().blit(screen,self.placement_camera)
        if self.paired_dragging_object is not None:
            self.paired_dragging_object.get_sprite().blit(screen,self.placement_camera)

    def magnetile_selected(self,magnetile):
        self.dragging_object=magnetile.my_copy()

    def turret_selected(self):
        #self.dragging_object=TurretDummy()
        #self.dragging_object=self.part_holder_ship
        self.part_holder_ship.part=Turret(self.part_holder_ship,attachment=Vec2d(0,0))
        self.dragging_object=self.part_holder_ship

    def cannon_selected(self):
        self.part_holder_ship.part=Cannon(self.part_holder_ship,attachment=Vec2d(0,0))
        self.dragging_object=self.part_holder_ship

    def torpedo_selected(self):
        self.part_holder_ship.part=TorpedoLauncher(self.part_holder_ship,attachment=Vec2d(0,0))
        self.dragging_object=self.part_holder_ship

    def check_snap(self):
        #if dragging an object, check if it is close to another object
        #for each magent joint pair, calculate the delta angle and distance to snap
        best_snap=None
        best_goodness=40
        for source_joint_pair in self.dragging_object.get_world_joint_pairs():            
            #for target_obj in self.objects:
                #for target_joint_pair in target_obj.get_world_joint_pairs():                    
            for target_joint_pair in self.the_ship.get_world_joint_pairs():
                    delta_angle=source_joint_pair.magnet1.normal.get_angle_between(-target_joint_pair.magnet2.normal)
                    delta_dist=target_joint_pair.magnet2.position-source_joint_pair.magnet1.position
                    goodness=delta_dist.length+20*abs(delta_angle)
                    #check if other magnet is close
                    
                    if goodness<best_goodness:
                        best_goodness=goodness
                        best_snap=(delta_dist,delta_angle)
        if best_snap is not None:            
            self.dragging_object.body.position+=best_snap[0]
            self.dragging_object.body.angle+=best_snap[1]
            if self.pair_mode:
                if self.paired_dragging_object is None:
                    self.paired_dragging_object=self.dragging_object.my_copy().invert()
                self.paired_dragging_object.body.position=Vec2d(-self.dragging_object.body.position[0],self.dragging_object.body.position[1])                
                self.paired_dragging_object.body.angle=-self.dragging_object.body.angle                    
            else:
                self.paired_dragging_object=None                    
            return
        self.paired_dragging_object=None
        #failing that, snap to center line
        if not self.pair_mode:
            if abs(self.dragging_object.body.position.x)<30:
                new_pos=Vec2d(0,self.dragging_object.body.position.y)
                self.dragging_object.body.position=new_pos
                return 
                #print("snap",best_snap)
        else:
            for source_joint_pair in self.dragging_object.get_world_joint_pairs():
                goodness=abs(source_joint_pair.magnet1.position.x)
                delta_angle=source_joint_pair.magnet1.normal.get_angle_between(Vec2d(1,0))
                if goodness<best_goodness:
                    best_goodness=goodness
                    best_snap=(Vec2d(-source_joint_pair.magnet1.position.x,source_joint_pair.magnet1.position.y),delta_angle)     
            if best_snap is not None:            
                self.dragging_object.body.position+=best_snap[0]
                self.dragging_object.body.angle+=best_snap[1]
                if self.pair_mode:
                    if self.paired_dragging_object is None:
                        self.paired_dragging_object=self.dragging_object.my_copy().invert()
                    self.paired_dragging_object.body.position=Vec2d(-self.dragging_object.body.position[0],self.dragging_object.body.position[1])                
                    self.paired_dragging_object.body.angle=-self.dragging_object.body.angle                    
                else:
                    self.paired_dragging_object=None                    
                return       

    def remove_ship(self):
        if len(self.the_ship.shape)>0:
            self.placement_space.remove(self.the_ship.body,*self.the_ship.shape)

    def add_ship(self):
        if len(self.the_ship.shape)>0:
           self.placement_space.add(self.the_ship.body,*self.the_ship.shape)

    def save_ship(self,filename):
        ship_dict=self.the_ship.to_dict()
        with open(filename, 'w') as file:
            yaml.dump(ship_dict, file)
    def load_ship(self,filename):
        with open(filename, 'r') as file:
            ship_dict = yaml.load(file, Loader=yaml.FullLoader)
            self.remove_ship()            
            self.the_ship.from_dict(ship_dict)
            self.add_ship()