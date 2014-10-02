import pyglet, random
from game import resources, physicalobject, matter, util

class Cell(physicalobject.PhysicalObject):

    def __init__(self,
                 min_size=0.0,
                 max_size=0.0,
                 name="Cell",
                 energy=25,
                 Color=(0, 0, 0),
                 *args,
                 **kwargs):

        
        if min_size == 0.0:
            self.min_size=random.randint(5,15)*0.1
        else:
            self.min_size = min_size
        if max_size == 0.0:
            self.max_size=random.randint(10,35)*0.1
        else:
            self.max_size = max_size

        super(Cell, self).__init__(img=resources.cell_image, *args, **kwargs)
        self.scale = self.min_size

        if Color == (0, 0, 0):
            self.Color = (192+random.randint(-80,10), 192+random.randint(-40, 20), 192+random.randint(-10, 50))
        else:
            self.Color = Color
        self._set_color(self.Color)

        # Counters: (Maybe reading time is better than this)
        self.time = 0
        self.Type = 'cell'

        self.mobile = True
        self.searching = False
        self.target = None
        self.search_radius = 10

        self.name = name
        self.step_size = 1
        self.scale_inv = 1.0/self.scale

        self.energy = energy
        self.energy_max = 100
        self.stamina = 100
        # Goes up slowly
        self.maturity = 10
        self.fertility_min = 15
        self.fertility_max = 60
        self.fertility_req = 90
        self.fertility_cost = int(0.5*self.fertility_req)
        self.fertile = False
        self.lifespan = 70
        self.new_obj = []


    def random(self):
        """ Random Walk code"""

        if random.random() < self.scale_inv:
            if bool(random.getrandbits(1)):
                if bool(random.getrandbits(1)):
                    dz = (1, 0)
                else:
                    dz = (-1, 0)
            else:
                if bool(random.getrandbits(1)):
                    dz = (0, 1)
                else:
                    dz = (0, -1)
            self.set_position(self.x + dz[0], self.y + dz[1])
        return 0


    def update(self, dt, objects = []):
        self.time += 1
        if self.energy >= self.fertility_req:
            self.energy += self.spawn()
            #and self.maturity >= self.fertility_min \
            #and self.maturity <= self.fertility_max:
        else:

            self.energy += self.move()
            self.energy += self.behavior(dt, objects)
            self.energy += self.grow()


            super(Cell, self).update(dt)
            if self.energy < 0:
                self.dead = True
            if self.maturity > self.lifespan:
                # Increasing chance of death after lifespan surpassed:
                if random.randint(1,self.maturity) > self.lifespan:
                    self.dead = True
            if self.dead == True:
                self.die()

    def hit_test(self, x, y):
        """ See if we go out of bounds """
        if x < self.x + self.image.width*self.scale/2 and \
            x > self.x - self.image.width*self.scale/2 and \
            y < self.y + self.image.height*self.scale/2 and \
            y > self.y - self.image.height*self.scale/2:
                return True
        else:
            return False



    def handle_collision_with(self, other_object):
        super(Cell, self).handle_collision_with(other_object)
        if "matter" in other_object.name and self.energy < self.energy_max - 10:
            self.energy += 10

        
    def spawn(self):
        print self.name, "spawns new offspring!", self.name+"_child" 
        self.new_obj.append(Cell( min_size = self.min_size,
                                  max_size = self.max_size,
                                  name = self.name+"_child",
                                  energy = int(self.fertility_cost*0.3),
                                  Color = self.Color,
                                  box = self.box,
                                  x = self.x + self.width * 0.5,
                                  y = self.y + self.height* 0.5,
                                  batch=self.batch))
        return -self.fertility_cost

    def move(self):
        return self.random()


    def behavior(self, dt, objects):
        """
        Action for one time-step that will require energy and stamina
        """
        # Determine when to start searching for food
        if self.target == None and self.searching == False:
            self.searching = bool(random.getrandbits(1))
            if self.searching == True:
                print self.name, "Begin searching for food"
        elif self.target == None and self.searching == True:
            return self.search(objects)
        else:
            # Target found
            if self.target.dead:
                print "Target is dead"
                self.target = None
                self.searching = False
            else:
                return self.pathfind(dt, self.target.x, self.target.y)
        return 0


    def search(self, objects):
        """
        Search for a target
        """
        if self.time%60 == 0:
            self.search_radius += 10

            for obj in [obj for obj in objects if obj.Type == 'matter']:
                if abs(obj.x - self.x) < self.search_radius:
                    if abs(obj.y - self.y) < self.search_radius:
                            if util.distance((obj.x, obj.y), (self.x, self.y)) < self.search_radius**2:
                                print self.name, " has found some food!"
                                self.target = obj
                                self.search_radius = 10
    


            return -2
        else:
            return 0


    def pathfind(self, dt, x, y):
        """
        Move towards target
        """
        if self.x < x:
            dx = random.randint(0,1)
        elif self.x > x:
            dx = random.randint(-1,0)
        else:
            dx = 0
        if self.y < y:
            dy = random.randint(0, 1)
        elif self.y > y:
            dy = random.randint(-1, 0)
        else:
            dy = 0
         
        if self.x == x and self.y == y:
            self.target = None
            self.searching = False
        else:
            self.set_position(self.x + dx, self.y + dy)

        if dt % 120 == 0:
            return -1
        else:
            return 0
            
            


    def grow(self):
        #if random.randint(0,100) == 0:
        if self.time%120 == 0:
            if self.scale < self.max_size:
                self.scale += 0.05
                self.maturity += 1
            return -1
        else:
            return 0


    def stats(self):
        print "\nname: ",     self.name
        print "energy: ",   self.energy
        print "stamina: ",  self.stamina
        print "maturity: ", self.maturity
        print "fertile: ",  self.fertile
        print "scale: ",    self.scale


    def die(self):
        self.new_obj.append( matter.Matter(name=self.name+"_corpse",
                                           scale = self.scale,
                                           box = self.box,
                                           x = self.x,
                                           y = self.y,
                                           batch=self.batch))


    def delete(self):
        super(Cell, self).delete()
