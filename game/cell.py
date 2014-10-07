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


        if min_size <= 0.2:
            self.min_size=random.randint(8,15)*0.1
        else:
            self.min_size = min_size
        if max_size <= 0.2:
            self.max_size=random.randint(16,35)*0.1
        else:
            self.max_size = max_size

        super(Cell, self).__init__(img=resources.cell_image, *args, **kwargs)
        self.scale = self.min_size

        if Color == (0, 0, 0):
            self.Color = (192+random.randint(-80,40), 192+random.randint(-80, 40), 192+random.randint(-10, 50))
        else:
            self.Color = Color
        self._set_color(self.Color)

        # Counters: (Maybe reading time is better than this)
        self.time = 0
        self.Type = 'cell'

        self.mobile = True
        self.searching = False
        self.target = None
        self.search_radius = 20

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

        self.spawn_cooldown = 1000
        self.spawn_ctr = self.spawn_cooldown

        # Wander
        self.direction = 0

        # Circle
        self.center = [0, 0]
        self.radius = 30


    def update(self, dt, objects = []):
        self.time += 1
        if self.energy >= self.fertility_req \
        and self.maturity >= self.fertility_min \
        and self.maturity <= self.fertility_max:
            self.energy += self.spawn()

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
        if other_object.Type == 'matter' and self.energy < self.energy_max - 10 and self.time % 10 == 0:
            # Eat the food!
            self.energy += 10
        if other_object.Type == 'cell':
            pass


    def spawn(self):
        self.spawn_ctr += -1
        if self.spawn_ctr <= 0:
            self.spawn_ctr = self.spawn_cooldown
            #print self.name, "spawns new offspring!", self.name+"_child"
            self.new_obj.append(Cell( min_size = self.min_size + random.randint(-5,5)*0.1,
                                      max_size = self.max_size + random.randint(-5,5)*0.1,
                                      name = self.name+"_child",
                                      energy = int(self.fertility_cost*0.8),
                                      Color = self.Color,
                                      box = self.box,
                                      x = self.x + self.width * 0.5,
                                      y = self.y + self.height* 0.5,
                                      batch=self.batch))
            return -self.fertility_cost
        else:
            return 0


    def move(self):
        if self.hungry() and self.target == None:
            return self.wander()
        elif self.hungry() and not self.target == None:
            return self.pathfind()
        else:
            return self.random()


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


    def wander(self):
        if random.randint(0,20) == 0:
            self.direction = random.randint(0,3)
        if self.direction == 0:
            self.set_position(self.x + 1, self.y + random.randint(-1,1))
        elif self.direction == 1:
            self.set_position(self.x - 1, self.y + random.randint(-1,1))
        elif self.direction == 2:
            self.set_position(self.x + random.randint(-1,1), self.y + 1)
        elif self.direction == 3:
            self.set_position(self.x + random.randint(-1,1), self.y - 1)

        if self.time%60 == 0:
            return -1
        else:
            return 0

    def circle(self):
        if random.randint(0,20) == 0:
            self.center[0] = self.x + random.randint(-30,30)
            self.center[1] = self.y + random.randint(-30,30)
        return 0



    def pathfind(self):
        """
        Move towards target
        """
        if self.target.dead:
            #print "Target is dead"
            self.target = None
            self.searching = False
            return 0
        else:
            if self.x < self.target.x:
                dx = random.randint(0,1)
            elif self.x > self.target.x:
                dx = random.randint(-1,0)
            else:
                dx = 0
            if self.y < self.target.y:
                dy = random.randint(0, 1)
            elif self.y > self.target.y:
                dy = random.randint(-1, 0)
            else:
                dy = 0

            if self.x == self.target.x and self.y == self.target.y:
                self.target = None
                self.searching = False
            else:
                self.set_position(self.x + dx, self.y + dy)

            if self.time % 240 == 0:
                return -1
            else:
                return 0


    def behavior(self, dt, objects):
        """
        Action for one time-step that will require energy and stamina
        """
        # Determine when to start searching for food
        if self.target == None and self.searching == False:
            self.searching = bool(random.getrandbits(1))
        elif self.target == None and self.searching == True:
            return self.search(objects)
        return 0


    def search(self, objects):
        """
        Search for a target
        """
        if self.time%30 == 0:
            # self.search_radius += 10
            # Faster, but less cool visually
            #for obj in [obj for obj in objects if obj.Type == 'matter']:
            #if self.clicked == True:
            self.inview = [self]

            for obj in objects:
                if abs(obj.x - self.x) < self.search_radius:
                    if abs(obj.y - self.y) < self.search_radius:
                            if util.distance((obj.x, obj.y), (self.x, self.y)) < self.search_radius**2:
                                self.inview.append(obj)
                                if obj.Type == 'matter':
                                    self.search_radius = 20
                                    self.target = obj

            return random.randint(-1,0)
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


    def hungry(self):
        return (self.energy < 60)

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
