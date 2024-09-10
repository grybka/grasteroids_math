from engine.GameObjects import *
from pymunk import Vec2d
import yaml

magnetile_scale=40
magnetile_density=0.05

def random_magnetile_color():
    return pygame.Color(random.choice(["blue2","firebrick2","gold","darkolivegreen4","darkorchid4"]))


magnetile_density=0.05
magnetile_scale=40
magnet_fraction=0.25

class MagnetileJoint:
    def __init__(self,position,polarity,normal):
        self.position=position
        self.polarity=polarity
        self.normal=normal

class MagnetileJointPair:
    def __init__(self,magnet1,magnet2):
        self.magnet1=magnet1
        self.magnet2=magnet2

#vertices must be in clockwise order
class Magnetile(GameObject):
    def __init__(self,position=Vec2d(0,0),vertices=[],color=None,angle=0):
        GameObject.__init__(self)
        self.vertices=[Vec2d(magnetile_scale*v[0],magnetile_scale*v[1]) for v in vertices]
        #generate magnets
        self.magnets=[]        
        self.joint_pairs=[]
        for i in range(len(self.vertices)):
            a=self.vertices[i]
            b=self.vertices[(i+1)%len(self.vertices)]
            direction=(b-a).normalized()
            normal=direction.perpendicular()            
            if (b-a).length<=math.sqrt(2)*magnetile_scale:                
                center=(a+b)/2                
                joint1=MagnetileJoint(center-direction*magnetile_scale*magnet_fraction,1,normal)
                joint2=MagnetileJoint(center+direction*magnetile_scale*magnet_fraction,-1,normal)
                self.magnets.append(joint1)
                self.magnets.append(joint2)
                self.joint_pairs.append(MagnetileJointPair(joint1,joint2))         
            else:                               
                center=(0.25*a+0.75*b)                                            
                normal=direction.perpendicular()            
                joint1=MagnetileJoint(center-direction*magnetile_scale*magnet_fraction,1,normal)
                joint2=MagnetileJoint(center+direction*magnetile_scale*magnet_fraction,-1,normal)
                self.magnets.append(joint1)
                self.magnets.append(joint2)
                self.joint_pairs.append(MagnetileJointPair(joint1,joint2))         
                center=(0.75*a+0.25*b)                                            
                normal=direction.perpendicular()            
                joint1=MagnetileJoint(center-direction*magnetile_scale*magnet_fraction,1,normal)
                joint2=MagnetileJoint(center+direction*magnetile_scale*magnet_fraction,-1,normal)
                self.magnets.append(joint1)
                self.magnets.append(joint2)
                self.joint_pairs.append(MagnetileJointPair(joint1,joint2))         
                

        #generate pymunk body
        self.body = pymunk.Body()
        self.body.position = position
        self.body.angle=angle
        self.shape = pymunk.Poly(self.body, self.vertices)
        self.shape.collision_type=COLLISION_TYPE_SHIP
        self.shape.density=magnetile_density
        self.shape.friction=0.5
        self.shape.elasticity=0.8
        #pick a color
        if color is None:
            self.color=random_magnetile_color()
        else:
            self.color=color
        self.sprite=MagnetileSprite(self)

    def get_points(self):
        ret=[]
        for v in self.vertices:
            ret.append( (v[0]/magnetile_scale,v[1]/magnetile_scale))
        return ret
    
    def get_vertices_worldspace(self):
        return [self.body.local_to_world(v) for v in self.vertices]

    def get_world_joint_pairs(self):
        ret=[]
        for pair in self.joint_pairs:
            ret.append(MagnetileJointPair(MagnetileJoint(self.body.local_to_world(pair.magnet1.position),pair.magnet1.polarity,pair.magnet1.normal.rotated(self.body.angle)),
                                          MagnetileJoint(self.body.local_to_world(pair.magnet2.position),pair.magnet2.polarity,pair.magnet2.normal.rotated(self.body.angle))))
        return ret
    
    def get_sprite(self):
        return self.sprite
        #return DebugPolySprite(self.shape.get_vertices(),self.color,self.body.position,self.body.angle)    
            
    def invert(self):
        points=self.get_points()
        points.reverse()
        new_vertices=[(-v[0],v[1]) for v in points]        
        return Magnetile(self.body.position,new_vertices)
    
    def my_copy(self):
        return Magnetile(self.body.position,self.get_points(),color=self.color,angle=self.body.angle)
    
    def to_dict(self):
        position=[self.body.position[0],self.body.position[1]]
        verts=[ [v[0],v[1]] for v in self.get_points()]
        color=[ self.color.r,self.color.g,self.color.b, self.color.a]
        return {"type":"magnetile","position":position,"angle": self.body.angle,"vertices":verts,"color":color}
    
    @staticmethod
    def from_dict(d):
        pos=Vec2d(d["position"][0],d["position"][1])
        color=None
        if "color" in d:
            color=pygame.Color(d["color"][0],d["color"][1],d["color"][2],d["color"][3])        
        ret=Magnetile(pos,d["vertices"],color=color)
        ret.set_angle(d["angle"])
        return ret
        

class SquareMagnetile(Magnetile):
    def __init__(self,position=Vec2d(0,0),color=None):
        points=[(-1/2,-1/2),(-1/2,1/2),(1/2,1/2),(1/2,-1/2)]
        Magnetile.__init__(self,position,points,color=color)

   
class RectMagnetile(Magnetile):
    def __init__(self,position=Vec2d(0,0),color=None):
        points=[(-1/2,-1),(-1/2,1),(1/2,1),(1/2,-1)]
        Magnetile.__init__(self,position,points,color)

  
class RightTriangleMagnetile(Magnetile):
    def __init__(self,position=Vec2d(0,0),color=None):
        #points=[(-magnetile_scale/2,-magnetile_scale/2),(-magnetile_scale/2,magnetile_scale/2),(magnetile_scale/2,-magnetile_scale/2)]
        points=[(-1/2,-1/2),(-1/2,1/2),(1/2,-1/2)]
        Magnetile.__init__(self,position,points,color)        

   
class EquilateralTriangleMagnetile(Magnetile):
    def __init__(self,position=Vec2d(0,0),color=None):
        points=[(-1/2,-1/2),(0,math.sqrt(3)/2-1/2),(1/2,-1/2)]
        Magnetile.__init__(self,position,points,color)

   
class IsocelesTriangleMagnetile(Magnetile):
    def __init__(self,position=Vec2d(0,0),color=None):
        points=[(-1/2,-1/2),(0,math.sqrt(15)/2-1/2),(1/2,-1/2)]
        Magnetile.__init__(self,position,points,color)

  
class TallRightTriangleMagnetile(Magnetile):
    def __init__(self,position=Vec2d(0,0),color=None):
        points=[(-1/2,-1/2),(-1/2,3/2),(1/2,-1/2)]
        Magnetile.__init__(self,position,points,color)

   
class MagnetileConstruction(GameObject):
    def __init__(self,magnetiles=[],re_center=False,shape_fname=None):
        GameObject.__init__(self)
        #Ideally, the magnetile position are all relative to the construction with angle zero
        if shape_fname is not None:
            self.magnetiles=[]
            with open(shape_fname,"r") as f:
                d=yaml.safe_load(f)                
                for m in d["magnetiles"]:
                    self.magnetiles.append(Magnetile.from_dict(m))
            
        else:
            self.magnetiles=magnetiles

        #generate pymunk body
        self.body = pymunk.Body()                
        #generate pymunk shapes
        self.shape = []
        for m in self.magnetiles:
            print("magnetile position",m.body.position)
            verts=m.get_vertices_worldspace()
            shape = pymunk.Poly(self.body, verts)
            shape.collision_type=COLLISION_TYPE_SHIP
            shape.density=magnetile_density
            shape.friction=0.5
            shape.elasticity=0.8
            self.shape.append(shape)
        if re_center:
            self.re_center()
        #generate sprite
        self.sprite=MagnetileConstructionSprite(self)
    
    def get_mass(self):
        return sum([s.mass for s in self.shape])
    
    def get_moment(self):
        moment=0
        for s in self.shape:
            moment+=s.moment+s.center_of_gravity.get_length_sqrd()*s.mass
        return moment

    def re_center(self):
        #find the center of mass
        total_mass=0
        center=Vec2d(0,0)
        for s in self.magnetiles:
            center+=s.body.local_to_world(s.shape.center_of_gravity)*s.shape.mass            
            total_mass+=s.body.mass
        center/=total_mass
        print("center of mass is",center)
        self.body.position=center
        for s in self.magnetiles:
            s.body.position-=center

    def to_dict(self):
        ret=[]
        for m in self.magnetiles:
            ret.append(m.to_dict())
        return {"type":"magnetile_construction","magnetiles":ret}    
    
    def get_bbox(self):
        #assumens center is at 0,0
        minx=1e9
        miny=1e9
        maxx=-1e9
        maxy=-1e9
        for m in self.magnetiles:
            for v in m.get_vertices_worldspace():
                minx=min(minx,v[0])
                miny=min(miny,v[1])
                maxx=max(maxx,v[0])
                maxy=max(maxy,v[1])               
        return (minx,miny,maxx,maxy)
        
    @staticmethod
    def from_dict(d):
        ret=[]
        for m in d["magnetiles"]:
            ret.append(Magnetile.from_dict(m))
        return MagnetileConstruction(ret)
        
    def save(self,filename):
        with open(filename,"w") as f:
            f.write(yaml.dump(self.to_dict()))
                
    def get_sprite(self):
        return self.sprite        
