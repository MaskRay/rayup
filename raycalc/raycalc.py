#!/usr/bin/env python

import pygtk, gtk, gtk.glade, sys
pygtk.require('2.0')

class Raycalc:
	def __init__(self):
		self.widget_tree = gtk.glade.XML(sys.path[0]+'/raycalc.glade', 'window1')
		self.widget_tree.get_widget('window1').set_title('Raycalc')
		dict = {'on_window1_destroy':gtk.main_quit,\
				'on_clr_btn_clicked':self.clr_btn_clicked,\
				'on_calc_btn_clicked':self.calc_btn_clicked,\
				'on_btn_clicked':self.btn_clicked}
		self.widget_tree.signal_autoconnect(dict)
	def main(self):
		gtk.main()
	def btn_clicked(self, widget, data = None):
		entry1 = self.widget_tree.get_widget('entry1')
		entry1.set_text(entry1.get_text()+widget.get_label())
	def clr_btn_clicked(self, widget, data = None):
		self.widget_tree.get_widget('entry1').set_text('')
	def calc_btn_clicked(self, widget, data = None):
		entry1 = self.widget_tree.get_widget('entry1')
		s = entry1.get_text().replace('/', './')
		try:
			entry1.set_text(str(eval(s)))
		except SyntaxError:
			pass

if __name__ == "__main__":
	Raycalc().main()
