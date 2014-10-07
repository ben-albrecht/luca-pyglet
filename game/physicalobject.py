import pyglet
from game import resources, util

class PhysicalObject(pyglet.sprite.Sprite):

    def __init__(self,
                 box=[384, 0, 1920, 1080],
                 name="physical object",
                 *args,
                 **kwargs):
        super(PhysicalObject, self).__init__(*args, **kwargs)
        # Eventually I'll make a window class with shared memory for physical objects to access
        #self.dimensions = [1920, 1080]

        self.mobile = False
        # TODO - only set true when object has moved
        self.moved = True
        self.box = box
        self.min_x = box[0] + self.image.width/2
        self.min_y = box[1] + self.image.height/2

        self.max_x = box[2] - self.image.width/2
        self.max_y = box[3] - self.image.height/2
        self.dx = 0
        self.dy = 0
        self.scale = 1.0
        self.dead = False
        self.new_obj = []
        self.time = 0

        # Clicking Mechanics
        self.clicked = False
        self.inview = [self]

        self.direction = 0

    def check_bounds(self):
        """
        Check boundaries of window
        """
        if self.x < self.min_x:
            self.x = self.min_x
            self.direction = 0
        elif self.x > self.max_x:
            self.x = self.max_x
            self.direction = 1
        if self.y < self.min_y:
            self.y = self.min_y
            self.direction = 2
        elif self.y > self.max_y:
            self.y = self.max_y
            self.direction = 3


    def collides_with(self, other_object):

        if util.distance_x(self.position, other_object.position) <= 50:
            collision_distance = (self.image.width * 0.5 * self.scale + \
                             other_object.scale * other_object.image.width * 0.5)
            if util.distance_x(self.position, other_object.position) <= collision_distance:
                if util.distance_y(self.position, other_object.position) <= collision_distance:
                    collision_distance_squared = collision_distance ** 2
                    actual_distance_squared = util.distance(self.position, other_object.position)
                    return (actual_distance_squared <= collision_distance_squared)
                else:
                    return False
            else:
                return False


    # Maybe handle collisions within each specific class?
    def handle_collision_with(self, other_object):
        #if "child" in self.name or "child" in other_object.name:
            #print "collision of", self.name, self.Type
            #print "and :", other_object.name, other_object.Type

        if other_object.Type == self.Type:
            # Bounce away
            if self.x <= other_object.x:
                dx = -self.image.width*0.5
            else:
                dx = self.image.width*0.5
            if self.y <= other_object.y:
                dy = -self.image.height*0.5
            else:
                dy = self.image.height*0.5
            self.set_position(self.x + dx, self.y + dy)
        else:
            pass


    def update(self, dt):
       self.check_bounds()


    def delete(self):
        """ Delete object"""
        #self.engine_sprite.delete()
        super(PhysicalObject, self).delete()



