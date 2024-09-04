import pygame

class SoundStore:
    def __init__(self):
        ...
        self.sounds={}
        self.channel_mapping={}

    def load_sounds(self):
        self.sounds["laser"]=pygame.mixer.Sound("sounds/Laser_00.wav")
        self.sounds["laser"].set_volume(0.1)
        #self.sounds["explosion"]=pygame.mixer.Sound("sounds/explosion_01.ogg")
        self.sounds["explosion"]=pygame.mixer.Sound("sounds/WarpDrive_00.wav")
        self.sounds["explosion"].set_volume(0.2)
        self.sounds["engine"]=pygame.mixer.Sound("sounds/SpaceShip_Engine_Large_Loop_00.wav")
        self.sounds["engine"].set_volume(0.5)
        pygame.mixer.set_reserved(0)
        self.channel_mapping["engine"]=pygame.mixer.Channel(0)

    def play_sound(self,sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print("Sound not found: "+sound_name)

    def get_channel(self,channel_name):
        if channel_name in self.channel_mapping:
            return self.channel_mapping[channel_name]
        else:
            print("Channel not found: "+channel_name)
            return None

    def loop_sound_on_channel(self,sound_name,channel_name):
        if sound_name in self.sounds:
            if channel_name in self.channel_mapping:
                self.channel_mapping[channel_name].play(self.sounds[sound_name],loops=-1)
            else:
                print("Channel not found: "+channel_name)
        else:
            print("Sound not found: "+sound_name)


_sound_store=SoundStore()

def get_sound_store():
    return _sound_store