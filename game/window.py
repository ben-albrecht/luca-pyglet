import pyglet, random, math
from pyglet.window import key
from game import resources, cell, util, rectangle, objmgr

class Window(pyglet.window.Window):
    """
    The 'main' Class of the game for now.
    This Class acts as the driver and calls
    all the other classes in the game
    """

    def __init__(self, *args, **kwargs):
        # Core Functionality
        self.dimensions = util.get_dimensions()
        self.Width = self.dimensions[0]/2
        self.Height = self.dimensions[1]/2
        self.Ratio = self.Width/float(self.Height)
        super(Window, self).__init__(self.Width,
                                     self.Height,
                                     caption='RandomWalk Version 1.0',
                                     resizable=True)

        self.batch = pyglet.graphics.Batch()
        self.menu_batch = pyglet.graphics.Batch()
        self.clicked_objects = []
        self.pause = False
        self.num_cells = 3
        self.num_matter = 100
        self.game_box = [(self.Width/5)+1,
                         0,
                         self.Width,
                         self.Height]
        self.ObjectManager = objmgr.ObjMgr(self.game_box, self.batch)
        self.ObjectManager.load(Type='cell', Num=self.num_cells)
        self.ObjectManager.load(Type='matter', Num=self.num_matter)
        rect = rectangle.Rectangle(0, 0, self.Width/5, self.Height, self.menu_batch)
        #title = rectangle.Rectangle(0, self.Height/5, self.Width/5, self.Height, self.batch)

        # Pushing event handler to stack
        self.key_handler = key.KeyStateHandler()
        self.event_handler = self.key_handler
        self.push_handlers(self.event_handler)

        # Cosmetics

        self.Fullscreen = False
        self.fps_display = pyglet.clock.ClockDisplay()
        #self.label = pyglet.text.Label(text = "Random Walk Version 1.0",
        #                         anchor_x = 'center',
        #                         x = self.Width / 2,
        #                         y = self.Height - 20,
        #                         batch = self.batch)

        self.lastobj = None
        # Prints
        print "Ratio", self.Ratio
        print "Dimensions: ", self.dimensions[0],"x", self.dimensions[1]


    def on_draw(self):
            self.clear() #clears the screen
            if not self.lastobj == None and not self.lastobj.Type == 'matter':
                for obj in self.lastobj.inview:
                    if not obj == None and obj.dead == False:
                        obj.draw()
            else:
                self.batch.draw()

            self.menu_batch.draw()
            self.fps_display.draw()


    def on_mouse_press(self, x, y, button, modifiers):
        targetclicked = False
        self.objects = self.ObjectManager.objects
        # Find out what was clicked
        for obj in self.objects:
            if obj.hit_test(x, y):
                self.undo_click()
                targetclicked = True
                self.lastobj = obj
                break

        self.handle_click(targetclicked)


    def handle_click(self, targetclicked):
        if targetclicked == False:
            self.undo_click()
        else:

            self.lastobj.stats()
            self.objcolor = self.lastobj.color
            self.lastobj._set_color((240, 30, 30))

            if not self.lastobj.Type == 'matter':
                # Change to POV of this object
                self.lastobj.clicked = True
                self.clicked = True
                print self.lastobj.inview


    def undo_click(self):
        """
        Undo everything that happened when we clicked
        """
        if not self.lastobj == None:
            self.lastobj.batch = self.batch
            self.lastobj._set_color(self.objcolor)
            self.lastobj.clicked = False
            self.clicked_objects = []
            self.lastobj = None


    def update(self, dt):
        # TODO: Encapsulate keyboard handling into separate methods

	self.dispatch_event('on_update', dt)
        if self.pause == True:
            return

        self.ObjectManager.update(dt)



    def on_key_press(self, symbol, modifier):
        super(Window, self).on_key_press(symbol, modifier)
        if symbol == key.SPACE:
            self.pause = not self.pause

        if symbol == key.P and self.Fullscreen == False:
            self.Fullscreen = True
            self.rescale(2.0, 2.0)
            self.set_fullscreen()
        if symbol == key.O and self.Fullscreen == True:
            self.Fullscreen = False
            self.rescale(0.5, 0.5)
            self.set_fullscreen(fullscreen=False)



    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)

        # Matain Ratio
  #      self.width = self.Ratio*height

  #      print "Old Window Width:", self.Width
  #      print "Old Window Height", self.Height
  #      print "New Window Width:", self.width
  #      print "New Window Height", self.height

  #      #self.rescale(float(self.width/self.Width), float(self.height/self.Height))

  #      self.Width = self.width
  #      self.Height = self.height


    def rescale(self, width, height):
        pyglet.gl.glScalef(width, height, 1.0)
        pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MAG_FILTER, pyglet.gl.GL_NEAREST)
        pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D, pyglet.gl.GL_TEXTURE_MIN_FILTER, pyglet.gl.GL_NEAREST)
