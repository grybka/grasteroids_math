import pygame
import yaml

class SpriteAnimationFileSet:
    def __init__(self,directory=None,file_prefix=None,frame_count=None,frame_time=None):
        self.directory=directory
        self.file_prefix=file_prefix
        self.frame_count=frame_count
        self.frame_time=frame_time

class SpriteAnimationsLoader:
    def __init__(self):
        self.animation_info={}
        self.animation_frames={}
        self.animation_info["explosion"]=SpriteAnimationFileSet("images/explosion","",9,0.050)
        self.animation_info["explosion2"]=SpriteAnimationFileSet("images/explosion2","e_",15,0.050)

        self.animation_info["laser_beam"]=SpriteAnimationFileSet("images/pulsating_beam","beam_",9,0.1)

    def load(self,file_set:SpriteAnimationFileSet):
        frames=[]
        for i in range(file_set.frame_count):
            fname=file_set.directory+"/"+file_set.file_prefix+"{:04d}".format(i)+".png"
            frames.append(pygame.image.load(fname))
        return frames
    
    def get_animation(self,animation_name):
        if animation_name not in self.animation_frames:
            self.animation_frames[animation_name]=self.load(self.animation_info[animation_name])
        return self.animation_frames[animation_name],self.animation_info[animation_name].frame_time



_sprite_animation_store=SpriteAnimationsLoader()

def get_sprite_animation_store():
    return _sprite_animation_store