#!/usr/bin/env python

from math import pi, cos, sin
from random import random, randrange
import pygtk, gtk, gtk.glade, sys, gobject
pygtk.require('2.0')

appname = 'Cellular Automata Presentation'
gladefile = 'cellular_automata.glade'
FRAME_DELAY = 100

class Pref_dialog:
    def __init__(self):
        self.wtree = gtk.glade.XML(gladefile, 'pref_dialog')

    def run(self):
        dialog = self.wtree.get_widget('pref_dialog')
        ret = dialog.run()
        max_num_entry = self.wtree.get_widget('max_num_entry')
        velocity_entry = self.wtree.get_widget('velocity_entry')
        try:
            max_num = int(max_num_entry.get_text())
        except ValueError:
            ret = gtk.RESPONSE_CANCEL
            max_num = -1
        try:
            velocity = int(velocity_entry.get_text())
        except ValueError:
            ret = gtk.RESPONSE_CANCEL
            velocity = -1
        dialog.destroy()
        return ret, max_num, velocity


height, width, size = 500, 900, 2

class Persons:

    class Person:
        def __init__(self):
            self.x, self.y, self.color = randrange(0, width), 0, (random(), random(), random())
            r = random()
            self.flag = 0 if self.x < 1./3*width else 2 if self.x > 2./3*width else 1
            if random() < 0.1:
                self.flag = 0 if r < 0.4 else 2 if r > 0.6 else 1

    def __init__(self, max_num, velocity):
        self.persons = [self.Person() for i in xrange(max_num/2)]
        self.max_num, self.velocity = max_num, velocity

    def run(self):
        persons2 = []
        num_out = 0
        exits = [(width/4-30, height*0.7), (width*0.5-30, height*0.7),
                (width*0.75-30, height*0.7)]
        for i in self.persons:
            mind = 1e8
            theta = 0
            u = (i.x, i.y)
            while theta < 2*pi:
                pos = (i.x+cos(theta)*10, i.y+sin(theta)*10)
                theta += pi/6
                if not (0 <= pos[0] < width and 0 <= pos[1] < height):
                    continue
                dist = (pos[0]-exits[i.flag][0])**2+(pos[1]-exits[i.flag][1])**2
                if dist < mind and random() < 0.7:
                    mind = dist
                    u = pos

            if mind > 60:
                persons2.append(i)
                persons2[-1].x = u[0]
                persons2[-1].y = u[1]
            else:
                num_out += 1

        num_in = min(self.velocity, self.max_num-len(persons2))
        if random() < 0.3: num_in = int(num_in*random())
        persons2.extend([self.Person() for i in xrange(num_in)])
        self.persons = persons2
        return num_in, num_out

class Cellular_automata:
    def __init__(self):
        self.wtree = gtk.glade.XML(gladefile, 'window1')

        dic = {'on_window1_destroy': gtk.main_quit,
                'on_menuitem_preferences_activate':
                   self.on_menuitem_preferences_activate,
                'on_darea_expose_event': self.on_darea_expose_event
                }
        self.wtree.signal_autoconnect(dic)
        self.window = self.wtree.get_widget('window1')
        self.window.set_title(appname)
        self.window.show_all()

        self.statusbar = self.wtree.get_widget('statusbar')
        self.statusbar_cr = self.statusbar.get_context_id('')

        gobject.timeout_add(FRAME_DELAY, self.on_timeout)

        max_num = 500
        velocity = 10
        self.persons = Persons(max_num, velocity)

    def run(self):
        gtk.main()

    def on_timeout(self):
        num_in, num_out = self.persons.run()
        self.statusbar.pop(self.statusbar_cr)
        self.statusbar.push(self.statusbar_cr, str(num_in)+' person(s) entered and '
                +str(num_out)+' person(s) left')

        self.wtree.get_widget('darea').queue_draw()
        gobject.timeout_add(FRAME_DELAY, self.on_timeout)

    def on_menuitem_preferences_activate(self, widget, data = None):
        pref_dialog = Pref_dialog()
        ret = pref_dialog.run()
        if ret[0] == gtk.RESPONSE_OK:
            max_num, velocity = ret[1], ret[2]
            self.persons = Persons(max_num, velocity)
        return True

    def on_darea_expose_event(self, widget, data):
        cr = widget.window.cairo_create()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(5)
        cr.translate(50, 50)

        width, height = 900, 500

        cr.move_to(900, 0)
        cr.line_to(900, 500)
        cr.move_to(0, 0)
        cr.line_to(0, 500)
        cr.line_to(900, 500)
        cr.stroke()

        for i in self.persons.persons:
            cr.set_source_rgb(i.color[0], i.color[1], i.color[2])
            cr.arc(i.x, i.y, size, 0, 2 * pi)
            cr.fill()

        cr.rectangle(width / 4 - 30, height * 0.7 - 30, 60, 60)
        cr.rectangle(width / 2 - 30, height * 0.7 - 30, 60, 60)
        cr.rectangle(width * 0.75 - 30, height * 0.7 - 30, 60, 60)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke_preserve()
        cr.set_source_rgb(1, 1, 1)
        cr.fill()

        return True


if __name__ == "__main__":
    Cellular_automata().run()
