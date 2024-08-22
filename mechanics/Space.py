from mechanics.Mechanics import *
#A Space is a collection of interacting objects

#An object has
# - A mechanics part that tells it how it responds to forces
# - A shape part that tells it how it interacts with other objects

class Space:
    def __init__(self):
        self.bodies=[]

    def add_body(self, object):
        self.bodies.append(object)

    def update(self, dt):
        for i in range(len(self.bodies)):
            for j in range(i+1, len(self.bodies)):
                self.interact(self.bodies[i], self.bodies[j])
        for body in self.bodies:
            body.update(dt)

    def interact(self, object1, object2):
        contacts=get_contacts(object1,object2)
        if len(contacts)==0:
            return #no interaction
        #For overlaps, the force will be proportional to the reduced mass
        reduced_mass=1/(1/object1.get_mass()+1/object2.get_mass())
        acceleration_base=50
        acceleration_per_unit_overlap=50
        #print("n contacts: ",len(contacts))
        for contact in contacts:
            weight=1/len(contacts)
            #print("contact point: ",contact)
            contact_point, normal, penetration=contact
            force=weight*normal*(acceleration_base+acceleration_per_unit_overlap*penetration)*reduced_mass
            object1.apply_force(-force,contact_point)
            object2.apply_force(force,contact_point)
            #print("contact!")
            
            
            

        