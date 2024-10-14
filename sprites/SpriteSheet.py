import yaml
import pygame

#clips apart a sprite sheet and returns individual sprites based off a yaml description

class SpriteSheet:
    def __init__(self,sheet_fname):
        print("loading sheet file from",sheet_fname)
        self.sheet_name=sheet_fname        
        self.sheet_surface=pygame.image.load(sheet_fname)        

    def load_sprite(self,sprite_name,info_object):    
        print("loading sprite",sprite_name)    
        rect=(0,0,self.sheet_surface.get_width(),self.sheet_surface.get_height() )
        if "rect" in info_object:
            rect = info_object["rect"]        
        return self.sheet_surface.subsurface(rect)                

class SpriteSheetStore:
    def __init__(self):
        self.loaded_sheets={}
        self.loaded_sprites={}
        self.sprite_info_file=None

    def preload_sprites(self):
        for sprite_name in self.sprite_info_file:
            self.get_sprite(sprite_name)

    def load_sheet_info(self,info_fname):
        print("loading sheet info from",info_fname)
        with open(info_fname, 'r') as file:
            self.sprite_info_file = yaml.safe_load(file)

    def load_sheet(self,sheet_name):
        self.loaded_sheets[sheet_name]=SpriteSheet(sheet_name)

    def get_sprite(self,sprite_name,scale=1):        
        if sprite_name in self.loaded_sprites:
            if scale==1:
                return self.loaded_sprites[sprite_name]
            else:            
                return pygame.transform.scale(self.loaded_sprites[sprite_name],(int(self.loaded_sprites[sprite_name].get_width()*scale),int(self.loaded_sprites[sprite_name].get_height()*scale)))  

        if sprite_name not in self.sprite_info_file:
            raise Exception("Sprite not found: "+sprite_name)
        if self.sprite_info_file[sprite_name]["file"] not in self.loaded_sheets:
            self.load_sheet(self.sprite_info_file[sprite_name]["file"])
        self.loaded_sprites[sprite_name]=self.loaded_sheets[self.sprite_info_file[sprite_name]["file"]].load_sprite(sprite_name,self.sprite_info_file[sprite_name])
        print("sprite {} scale {}".format(sprite_name,scale))
        if scale==1:
            return self.loaded_sprites[sprite_name]
        else:            
            return pygame.transform.scale(self.loaded_sprites[sprite_name],(int(self.loaded_sprites[sprite_name].get_width()*scale),int(self.loaded_sprites[sprite_name].get_height()*scale)))        

_sprite_store=SpriteSheetStore()

def get_sprite_store():
    return _sprite_store