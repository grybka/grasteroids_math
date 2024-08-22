#temporary sprites made from geometric objects
from mechanics.Vector2D import Vector2D
from mechanics.Mechanics import *
from sprites.Sprite import *

def get_sprite_from_body(body,color=(255,255,255)):
    if isinstance(body,CircleBody2D):
        return CircleSprite(radius=body.radius,world_position=body.get_position(),color=color)
    if isinstance(body,PolygonBody2D):
        return PolygonSprite(vertices=body.vertices,world_position=body.get_position(),color=color,angle=body.get_angle())
    elif isinstance(body,CompositeBody2D):
        sprite=CompositeSprite()
        for subbody in body.bodies:
            sprite.add_sprite(get_sprite_from_body(subbody))
        return sprite
    return None