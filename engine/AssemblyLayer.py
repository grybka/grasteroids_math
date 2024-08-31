import pygame
from sprites.Sprite import *
from engine.GameObjects import *
from engine.Ship import *
import pymunk
from sprites.Background import *
from engine.Magnetile import *
from datetime import datetime

#For assembling magnetile ships

#Left side: list of magnetile types
#right side: place to put them down
#click and drag to place magnetile
#when they get close, they snap together

class Button:
    def __init__(self,rect,name=None):
        self.rect=rect
        self.name=name

    def draw(self,screen):
        pygame.draw.rect(screen,(255,255,255),self.rect,2)

    def point_in_button(self,pos):
        if pos[0]>self.rect[0] and pos[0]<self.rect[0]+self.rect[2] and pos[1]>self.rect[1] and pos[1]<self.rect[1]+self.rect[3]:
            return True
        return False

class TextButton(Button):
    def __init__(self,rect,text,name=None):
        Button.__init__(self,rect,name)
        self.text=text

    def draw(self,screen):
        Button.draw(self,screen)        
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, 1, (255,255,255))
        screen.blit(text, (self.rect[0]+10,self.rect[1]+10))

class ColorButton(Button):
    def __init__(self,rect,color,name=None):
        Button.__init__(self,rect,name)
        self.color=color

    def draw(self,screen):
        Button.draw(self,screen)        
        pygame.draw.rect(screen,self.color,self.rect)



class AssemblyLayer:
    def __init__(self,clock):
        self.clock=clock
        ...
        self.divider_x=400
        ...
        self.left_camera=Camera()
        self.choice_space = pymunk.Space()
        self.magnetile_choices=[]
        self.choice_y_spacing=100
        self.choice_last_y=-400
        self.choice_last_x=50
        self.add_choice(SquareMagnetile())
        self.add_choice(RectMagnetile())
        self.add_choice(RightTriangleMagnetile())
        self.add_choice(EquilateralTriangleMagnetile())
        self.add_choice(IsocelesTriangleMagnetile())
        self.add_choice(TallRightTriangleMagnetile())
        ...
        self.dragging_object=None
        ...
        self.placement_space = pymunk.Space()
        self.placement_camera=Camera()   
        #self.drag_camera=Camera()
        self.objects =[]     

        self.choice_space.step(1/1000.0)   
        ...
        self.buttons=[]
        self.buttons.append(TextButton((10,10,100,50),"Save","save"))        
        self.colors=["blue2","firebrick2","gold","darkolivegreen4","darkorchid4"]
        for color in self.colors:
            print("color",color)
            self.buttons.append(ColorButton((10,10+60*len(self.buttons),100,50),color,"color"))


    def add_choice(self,choice):
        self.choice_last_y+=self.choice_y_spacing
        choice.body.position=Vec2d(self.choice_last_x,self.choice_last_y)
        self.choice_space.add(choice.body,choice.shape)
        self.magnetile_choices.append(choice)    
    
    def left_space_to_right_space(self,world_position):
        screen_position=self.left_camera.get_screen_position(world_position)
        return self.placement_camera.get_world_position( (screen_position[0]-self.divider_x,screen_position[1]) )

    def update(self,ticks):
        if self.dragging_object is not None:
            pos=pygame.mouse.get_pos() 
            world_pos=self.placement_camera.get_world_position(pos)
            self.dragging_object.body.position=world_pos
            self.check_snap()


    def check_snap(self):
        #if dragging an object, check if it is close to another object
        #for each magent joint pair, calculate the delta angle and distance to snap
        best_snap=None
        best_goodness=40
        for source_joint_pair in self.dragging_object.get_world_joint_pairs():
            for target_obj in self.objects:
                for target_joint_pair in target_obj.get_world_joint_pairs():                    
                    delta_angle=source_joint_pair.magnet1.normal.get_angle_between(-target_joint_pair.magnet2.normal)
                    delta_dist=target_joint_pair.magnet2.position-source_joint_pair.magnet1.position
                    goodness=delta_dist.length+20*abs(delta_angle)
                    #check if other magnet is close
                    
                    if goodness<best_goodness:
                        best_goodness=goodness
                        best_snap=(delta_dist,delta_angle)
        if best_snap is not None:
            if best_snap[1]!=0:
                print("snap",best_snap)
                print("len self objects",len(self.objects))
            self.dragging_object.body.position+=best_snap[0]
            self.dragging_object.body.angle+=best_snap[1]
            #print("snap",best_snap)

                    
        ...

    def add_to_placement_space(self,obj):
        if isinstance(obj,MagnetileConstruction):
            #autodisassimble the magnetile construction
            for o in obj.magnetiles:
                self.add_to_placement_space(o)
            return
        self.placement_space.add(obj.body,obj.shape)
        self.objects.append(obj)

    def button_clicked(self,button):
        if button.name=="save":
            # get current date and timels 
            current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M")
            #print("Current date & time : ", current_datetime)
            
            # convert datetime obj to string
            str_current_datetime = str(current_datetime)
            
            # create a file object along with extension
            fname = str_current_datetime+".yaml"
            #fname="test.yaml"
            print("saving to {}".format(fname))
            MagnetileConstruction(self.objects).save(fname)
        if button.name=="color":
            for choice in self.magnetile_choices:
                choice.color=pygame.Color(button.color)


    def handle_event(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_s:
                fname="test.yaml"
                print("saving to {}".format(fname))
                MagnetileConstruction(self.objects).save(fname)  
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:                
                pos=pygame.mouse.get_pos()
                #first see if its a button
                for button in self.buttons:
                    if button.point_in_button(pos):
                        self.button_clicked(button)                        
                        break
                #if left of the divider, pick up a magnetile
                if pos[0]<self.divider_x:
                    world_pos=self.left_camera.get_world_position(pos)                    
                    for obj in self.magnetile_choices:
                        pq=obj.shape.point_query(world_pos)
                        if pq.distance<0: 
                            self.dragging_object=obj.get_of_type()                                     
                            break
                #if right of the divider and carrying a magnetile, place it
                elif pos[0]>self.divider_x and self.dragging_object is not None:
                    obj=self.dragging_object
                    self.add_to_placement_space(obj)
                    
                    self.dragging_object=None
                #if right of the divider and not carrying a magnetile, pick up the magnetile
                elif pos[0]>self.divider_x:
                    world_pos=self.placement_camera.get_world_position(pos)
                    for obj in self.objects:
                        pq=obj.shape.point_query(world_pos)
                        if pq.distance<0: 
                            self.placement_space.remove(obj.body,obj.shape)
                            self.objects.remove(obj)
                            self.dragging_object=obj
                            break
            if event.button==4:
                if self.dragging_object is not None:
                    self.dragging_object.body.angle+=0.1
                
            if event.button==5:
                if self.dragging_object is not None:
                    self.dragging_object.body.angle-=0.1

            if event.button==2:
                if self.dragging_object is not None:
                    self.dragging_object=self.dragging_object.invert()

            if event.button==3: #remove object
                if self.dragging_object is None:
                    pos=pygame.mouse.get_pos()
                    world_pos=self.placement_camera.get_world_position(pos)
                    for obj in self.objects:
                        pq=obj.shape.point_query(world_pos)
                        if pq.distance<0: 
                            self.placement_space.remove(obj.body,obj.shape)
                            self.objects.remove(obj)
                            break
                else:
                    self.dragging_object=None
                    
                
                
                                                
                    

    def draw(self,screen):
        self.left_camera.set_screen(screen.subsurface(0,0,self.divider_x,screen.get_height()))
        self.placement_camera.set_screen(screen)
        #self.placement_camera.set_screen(screen.subsurface(self.divider_x,0,screen.get_width()-self.divider_x,screen.get_height()))
        #self.drag_camera.set_screen(screen)
        #print("self.drag_camera.position",self.drag_camera.position)
        #print("self.placement_camera.position",self.placement_camera.position)



        screen.fill((0,0,0))

        #draw the left side
        self.draw_left(screen.subsurface(0,0,self.divider_x,screen.get_height()))
        #draw the right side
        self.draw_right(screen)
        ...
        #draw the divider
        pygame.draw.line(screen,(255,255,255),(self.divider_x,0),(self.divider_x,screen.get_height()),2)
        #draw the buttons
        for button in self.buttons:
            button.draw(screen)
        #draw the dragging object
        if self.dragging_object is not None:
            #print("dragging object positoin",self.dragging_object.body.position)
            self.dragging_object.get_sprite().blit(screen,self.placement_camera)

    def draw_left(self,screen):
        for obj in self.magnetile_choices:
            obj.get_sprite().blit(screen,self.left_camera)  

    def draw_right(self,screen):
        for obj in self.objects:
            obj.get_sprite().blit(screen,self.placement_camera)  
        

        