import pygame
from sprites.Sprite_To_Geometry import *
from sprites.SpriteSheet import get_sprite_store
import yaml

get_sprite_store().load_sheet_info("config/sprites.yaml")

output_fname="config/sprite_geometry.yaml"
output_data={}

for sprite_name in get_sprite_store().sprite_info_file:
    sprite=get_sprite_store().get_sprite(sprite_name)
    output_data[sprite_name]={}
    print(sprite_name,sprite.get_width(),sprite.get_height())
    circle_radius,circle_goodness=sprite_to_circle(sprite)
    print("Circle:",circle_radius,circle_goodness)
    square_radius,square_goodness=sprite_to_square(sprite)
    print("Square:",square_radius,square_goodness)
    if circle_goodness>square_goodness:
        print("Circle is better")
        output_data[sprite_name]["type"]="circle"
        output_data[sprite_name]["radius"]=circle_radius
    else:
        print("Square is better")
        output_data[sprite_name]["type"]="square"
        output_data[sprite_name]["radius"]=square_radius

with open(output_fname, 'w') as file:
    yaml.dump(output_data, file)
    print("Wrote to",output_fname)    

   


