import pyglet
import random
from game import cell, matter

class ObjMgr():
    """
    Class to add new objects into game window
    that do not spawn from other game objects
    """
    def __init__(self, box,  Batch):
        """
        Inialized with a running list of objects
        """
        self.box = box
        self.xmin = box[0]
        self.ymin = box[1]
        self.xmax = box[2]
        self.ymax = box[3]
        self.Batch = Batch
        # Counters
        self.counter_type = []
        self.counter = [0, 0]
        # objects
        self.objects = []
        self.objects_x = []
        self.objects_y = []
        self.objects_type = []


        self.types = {'cell'   : cell.Cell,
                      'matter' : matter.Matter}

        self.indices = {'cell'   : 0,
                         'matter' : 1}





    def load(self, Type='cell', Num=10):
        while self.counter[self.indices[Type]] < Num:
            new_obj = self.types[Type](box=self.box,
                                name=Type+str(self.counter[self.indices[Type]]),
                                x=random.randint(self.xmin, self.xmax),
                                y=random.randint(self.ymin, self.ymax),
                                batch=self.Batch)

            collides = False
            for i in xrange(len(self.objects)):
                other_obj = self.objects[i]
                if new_obj.collides_with(other_obj):
                    collides = True
                    break
            if not collides:
                self.objects.append(new_obj)
                self.counter[self.indices[Type]] += 1


    def update(self, dt):


        # Check collisions from last dt
        self.check_collisions()

        # Start list of objects to add
        to_add = []

        # Update objects for this dt
        to_add = self.update_objects(dt, to_add)

        # Remove objects for this dt
        to_add = self.remove_objects(to_add)

        # Spawn matter if necessary
        # to_add = self.spawn_matter(to_add)

        # Add objects for this dt
        self.objects.extend(to_add)





    def spawn_matter(self, to_add):
        # Doesn't work
        while self.counter[1]*5 < self.counter[0]:
            new_obj = self.types['matter'](box=self.box,
                                name='matter'+str(self.counter[self.indices['matter']]),
                                x=random.randint(self.xmin, self.xmax),
                                y=random.randint(self.ymin, self.ymax),
                                batch=self.Batch)
            to_add.extend(new_obj)
            #self.objects.append(new_obj)
            self.counter[self.indices['matter']] += 1
        return to_add


    def check_collisions(self):
        # Efficiency:
        # (1) Only if an object is in self.has_moved[ ] will they check collision
        # (2) Chop up game window into grid, and only check collisions with grid
        for i in xrange(len(self.objects)):
            if self.objects[i].Type == 'cell':
                for j in xrange(1, len(self.objects)):
                    if not self.objects[i] == self.objects[j]:
                        obj_1 = self.objects[i]
                        obj_2 = self.objects[j]
                        if not obj_1.dead and not obj_2.dead:
                            if obj_1.collides_with(obj_2):
                                obj_1.handle_collision_with(obj_2)
                                obj_2.handle_collision_with(obj_1)


    def update_objects(self, dt, to_add):
        # Update every animate object:
        for obj in [obj for obj in self.objects if obj.mobile]:
            if obj.searching:
                obj.update(dt, self.objects)
            else:
                obj.update(dt)
            to_add.extend(obj.new_obj)
            obj.new_obj = []


        # Update every inanimate object:
        for obj in [obj for obj in self.objects if not obj.mobile]:
            obj.update(dt)
            to_add.extend(obj.new_obj)
            obj.new_obj = []
        return to_add


    def remove_objects(self, to_add):
        # Remove any objects that died from objects and call obj.delete()
        # If dying object is adding new objects, add them here as well
        for to_remove in [obj for obj in self.objects if obj.dead]:
             to_add.extend(obj.new_obj)
             to_remove.delete()
             self.objects.remove(to_remove)
        return to_add
