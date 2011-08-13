#!/usr/bin/env python

import gtk, pygtk, gtk.glade, sys

class LinearProgramming:
	def __init__(self, n):
		self.n = n

	def pivot(self, l, e):
		for j in self.N:
			if j != e:
				self.a[e][j] = self.a[l][j]/float(self.a[l][e])
		self.a[e][l] = 1./self.a[l][e]

		self.b[e] = float(self.b[l])/self.a[l][e]
		for i in self.B:
			if i == l: continue
			self.b[i] = self.b[i]-self.a[i][e]*self.b[e]
			for j in self.N:
				if j != e:
					self.a[i][j] = self.a[i][j]-self.a[i][e]*self.a[e][j]
			self.a[i][l] = -self.a[i][e]*self.a[e][l]

		self.v = self.v+self.c[e]*self.b[e]
		for j in self.N:
			if j != e:
				self.c[j] = self.c[j]-self.c[e]*self.a[e][j]
		self.c[l] = -self.c[e]*self.a[e][l]

		self.N.remove(e)
		self.N.append(l)
		self.B.remove(l)
		self.B.append(e)

	def simplex(self):
		while True:
			e = -1
			for j in self.N:
				if self.c[j] > 0:
					e = j
					break
			else: break
			delta = -1
			for i in self.B:
				if self.a[i][e] > 0:
					t = float(self.b[i])/self.a[i][e]
					if delta == -1 or t < delta:
						delta = t
						l = i
			if delta == -1:
				return ()
			self.pivot(l, e)

	def main(self):
		#check if the initial basic solution is feasible
		k = 0
		for i in self.B:
			if self.b[i] < self.b[k]:
				k = i
		if self.b[k] >= 0:
			if self.simplex() == ():
				return 'unbounded',
			ret = [0.]*self.n
			for i in self.B:
				ret[i] = self.b[i]
			return 'ok', self.v, ret

		#set x_n
		object = self.v, self.c
		self.v = 0.
		self.c = [0]*self.n
		self.c.append(-1)
		self.b.append(0)
		self.a.append([0]*self.n)
		for i in self.a:
			i.append(-1)
		self.N.append(self.n)

		#get feasible soluion
		self.pivot(k, self.n)
		self.simplex()

		#get optimizing solution
		if abs(self.v) < 1E-6:
			self.v, self.c = object
			if self.n in self.N: self.N.remove(self.n)
			if self.n in self.B: self.B.remove(self.n)
			for i in self.B:
				self.v = self.v+self.c[i]*self.b[i]
				for j in self.N:
					self.c[j] = self.c[j]-self.c[i]*self.a[i][j]
			if self.simplex() == ():
				return 'unbounded',
			ret = [0.]*self.n
			for i in self.B:
				ret[i] = self.b[i]
			return 'ok', self.v, ret
		else:
			return 'infeasible',

class Raylps:
	def __init__(self):
		self.wtree = gtk.glade.XML(sys.path[0]+'/raylps.glade', 'window1')
		self.wtree.get_widget('window1').set_title('MasterRay Linear Programming Solver')
		dict = {'on_window1_destroy':gtk.main_quit,\
				'on_btn_ok_clicked':self.on_btn_ok_clicked,
				'on_btn_solve_clicked':self.on_btn_solve_clicked}
		self.wtree.signal_autoconnect(dict)
		self.tooltips = gtk.Tooltips()
		self.tooltips.set_tip(self.wtree.get_widget('entry_n'), 'number of variables(variables must be nonnegative)')
		self.tooltips.set_tip(self.wtree.get_widget('entry_m'), 'number of inequalities')
		self.tooltips.set_tip(self.wtree.get_widget('btn_ok'), 'new LP problem')
		self.tooltips.set_tip(self.wtree.get_widget('btn_solve'), 'solve the LP problem')

		self.table_lp = None
		self.n = 0
		self.m = 0

	def main(self):
		gtk.main()

	def on_btn_ok_clicked(self, widget, data = None):
		if self.table_lp != None:
			self.table_lp.destroy()
			self.table_result.destroy()
		self.n = int(self.wtree.get_widget('entry_n').get_text())
		self.m = int(self.wtree.get_widget('entry_m').get_text())
		if self.n <= 0 or self.m <= 0:
			return

		#table_lp
		self.table_lp = gtk.Table(self.m+1, 3*self.n+2)
		self.wtree.get_widget('table1').attach(self.table_lp, 0, 1, 1, 2, 0, 0)
		self.tooltips.set_tip(self.table_lp, 'line 1: objective function\nline 2~m+1: restrictions')
		self.entry_c = []
		self.entry_b = []
		self.entry_a = []

		for i in xrange(self.n):
			self.entry_c.append(gtk.Entry())
			self.entry_c[i].set_width_chars(6)
			self.table_lp.attach(self.entry_c[i], i*3, i*3+1, 0, 1, 0, 0)
			self.table_lp.attach(gtk.Label('x'+str(i+1)), i*3+1, i*3+2, 0, 1, 0, 0)
			self.table_lp.attach(gtk.Label('+'), i*3+2, i*3+3, 0, 1, 0, 0)
		self.entry_v = gtk.Entry()
		self.entry_v.set_width_chars(5)
		self.table_lp.attach(self.entry_v, 3*self.n, 3*self.n+1, 0, 1, 0, 0)

		for j in xrange(self.m):
			self.entry_a.append([])
			for i in xrange(self.n):
				self.entry_a[j].append(gtk.Entry())
				self.entry_a[j][i].set_width_chars(6)
				self.table_lp.attach(self.entry_a[j][i], i*3, i*3+1, j+1, j+2, 0, 0)
				self.table_lp.attach(gtk.Label('x'+str(i+1)), i*3+1, i*3+2, j+1, j+2, 0, 0)
				self.table_lp.attach(gtk.Label('<=' if i == self.n-1 else '+'), i*3+2, i*3+3, j+1, j+2, 0, 0)
			self.entry_b.append(gtk.Entry())
			self.entry_b[j].set_width_chars(5)
			self.table_lp.attach(self.entry_b[j], 3*self.n, 3*self.n+1, j+1, j+2, 0, 0)


		#table_result
		self.entry_x = []
		self.table_result = gtk.Table(1, self.n*2+2)
		self.wtree.get_widget('table1').attach(self.table_result, 0, 1, 3, 4, 0, 0)
		self.table_result.attach(gtk.Label('maximum='), 0, 1, 0, 1, 0, 0)
		self.entry_result = gtk.Entry()
		self.entry_result.set_width_chars(10)
		self.table_result.attach(self.entry_result, 1, 2, 0, 1, 0, 0)
		for i in xrange(self.n):
			self.table_result.attach(gtk.Label('x'+str(i+1)+'='), i*2+2, i*2+3, 0, 1, 0, 0)
			self.entry_x.append(gtk.Entry())
			self.entry_x[i].set_width_chars(5)
			self.table_result.attach(self.entry_x[-1], i*2+3, i*2+4, 0, 1, 0, 0)
		
		self.wtree.get_widget('table1').show_all()

	def on_btn_solve_clicked(self, widget, data = None):
		lp = LinearProgramming(self.n+self.m)
		n = self.n+self.m
		lp.a = [[0. for j in xrange(n)] for i in xrange(n)]
		lp.b = [0.]*n
		lp.c = [0.]*n
		lp.N = range(self.n)
		lp.B = range(self.n, self.n+self.m)

		try:
			lp.v = float(self.entry_v.get_text())
			for i in xrange(self.n):
				lp.c[i] = float(self.entry_c[i].get_text())
			for i in xrange(self.m):
				lp.b[self.n+i] = float(self.entry_b[i].get_text())
			for i in xrange(self.m):
				for j in xrange(self.n):
					lp.a[self.n+i][j] = float(self.entry_a[i][j].get_text())
		except Exception:
			return

		ret = lp.main()
		if ret[0] == 'ok':
			self.entry_result.set_text(str(ret[1]))
			for i in xrange(self.n):
				self.entry_x[i].set_text(str(ret[2][i]))
		else:
			self.entry_result.set_text(ret[0])

if __name__ == '__main__':
	Raylps().main()
