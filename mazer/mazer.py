#!/usr/bin/env python

from sys import stdout
from random import randrange, shuffle
import gtk

BORDER = 10
LENGTH = 24

class mazer():
    def __init__(self, maxw, maxh):
        self.maxw, self.maxh = maxw, maxh
        self.map = [[False for c in xrange(self.maxw*2+1)] for r in xrange(self.maxh*2+1)]
        self.map[randrange(1, self.maxh*2, 2)][0] = True
        self.map[randrange(1, self.maxh*2, 2)][self.maxw*2] = True
        self.DFS(randrange(1, self.maxw*2, 2), randrange(1, self.maxh*2, 2))

    def run(self):
        window = gtk.Window()
        window.set_title('mazer')
        window.connect('destroy', gtk.main_quit)

        darea = gtk.DrawingArea()
        darea.set_size_request(LENGTH*self.maxw+BORDER*2, LENGTH*self.maxh+BORDER*2)
        darea.connect('expose_event', self.expose)
        window.add(darea)

        window.show_all()
        gtk.main()

    def DFS(self, x, y):
        self.map[y][x] = True
        ds = [(1,0),(0,1),(-1,0),(0,-1)]
        shuffle(ds)
        for d in ds:
            if 0 <= x+d[0]*2 < self.maxw*2 and 0 <= y+d[1]*2 < self.maxh*2 and not self.map[y+d[1]*2][x+d[0]*2]:
                self.map[y+d[1]][x+d[0]] = True
                self.DFS(x+d[0]*2, y+d[1]*2)

    def expose(self, widget, data):
        for y in xrange(self.maxh+1):
            for x in xrange(self.maxw):
                if not self.map[y*2][x*2+1]:
                    widget.window.draw_line(widget.style.black_gc, BORDER+x*LENGTH, BORDER+y*LENGTH, BORDER+(x+1)*LENGTH, BORDER+y*LENGTH)
        for y in xrange(self.maxh):
            for x in xrange(self.maxw+1):
                if not self.map[y*2+1][x*2]:
                    widget.window.draw_line(widget.style.black_gc, BORDER+x*LENGTH, BORDER+y*LENGTH, BORDER+x*LENGTH, BORDER+(y+1)*LENGTH)


if __name__ == '__main__':
    mazer(12, 13).run()
