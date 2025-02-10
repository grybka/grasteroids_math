import pygame
import pymunk
from sprites.Sprite import *
from engine.MagnetileShip import *
from gui.DesignerMenus import *

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
        self.the_ship=get_ship_factory().get_ship(random.choice(enemy_choices))
        #self.the_ship=MagnetileShip()
        self.selection_window=MagnetileDesigner(self.ui_manager,self)
        #self.selection_window=MagnetileSelection(self.ui_manager,self)

        self.dragging_object=None

    def process_event(self, event):
        handled = super().process_event(event)
    #def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:         
                if self.dragging_object is not None:
                    print("adding magnetise")
                    #attach the dragging object to the ship
                    self.the_ship.add_magnetile(self.dragging_object)
                    self.dragging_object=None
        return False

    def update(self,ticks):
        if self.dragging_object is not None:
            pos=pygame.mouse.get_pos() 
            world_pos=self.placement_camera.get_world_position(pos)
            self.dragging_object.body.position=world_pos
            #TODO need to think about how to represent ship first
            self.check_snap()          

    def draw(self):
        screen=self.game_surface_element.image
        self.placement_camera.set_screen(screen)
        screen.fill((0,0,0))

        self.the_ship.get_sprite().blit(screen,self.placement_camera)
        #draw the dragging object
        if self.dragging_object is not None:
            self.dragging_object.get_sprite().blit(screen,self.placement_camera)

    def magnetile_selected(self,magnetile):
        self.dragging_object=magnetile.my_copy()

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
            #print("snap",best_snap)