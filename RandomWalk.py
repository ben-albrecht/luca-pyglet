import pyglet
from game import window, util

PROFILE = True
MEM_PROFILE = False

if util.module_exists('cProfile') and util.module_exists('pstats'):
    import cProfile
    import pstats
else:
    PROFILE = False
   
if util.module_exists('memory_profiler'):
    from memory_profiler import profile
    #import memory_profiler
else:
    MEM_PROFILE = False

win = window.Window()


def main():
    pyglet.clock.schedule_interval(win.update, 1/60.0)
    pyglet.app.run()


if __name__ == '__main__':
    # Profiling
    if PROFILE == True:
        print "PROFILE = True"
        cProfile.run('main()', 'restats')
        p = pstats.Stats('restats')
        #p.strip_dirs().sort_stats('cumulative').print_stats(15)
        p.strip_dirs().sort_stats('tottime').print_stats(15)
    else:
        main()
    

