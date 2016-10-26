#!/usr/bin/python
# -*- coding: utf-8 -*-

# import cairocffi as cairo
# from cairocffi import OPERATOR_SOURCE

import cairo as cairo
from cairo import OPERATOR_SOURCE

from numpy.random import random
from numpy import pi
from numpy import sqrt
from numpy import linspace
from numpy import arctan2
from numpy import cos
from numpy import sin
from numpy import column_stack
from numpy import square
from numpy import array
# from numpy import reshape
# from numpy import floor


TWOPI = pi*2


class Render(object):

  def __init__(self,n, back, front):

    self.n = n
    self.front = front
    self.back = back
    self.pix = 1./float(n)

    self.colors = []
    self.ncolors = 0
    self.num_img = 0

    self.__init_cairo()

  def __init_cairo(self):

    sur = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.n, self.n)
    ctx = cairo.Context(sur)
    ctx.scale(self.n, self.n)

    self.sur = sur
    self.ctx = ctx

    self.clear_canvas()

  def clear_canvas(self):

    ctx = self.ctx

    ctx.set_source_rgba(*self.back)
    ctx.rectangle(0, 0, 1, 1)
    ctx.fill()
    ctx.set_source_rgba(*self.front)

  def write_to_png(self, fn):

    self.sur.write_to_png(fn)
    self.num_img += 1

  def set_front(self, c):

    self.front = c
    self.ctx.set_source_rgba(*c)

  def set_back(self, c):

    self.back = c

  def set_line_width(self, w):

    self.ctx.set_line_width(w)

  def line(self, x1, y1, x2, y2):

    ctx = self.ctx

    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()

  def triangle(self, x1, y1, x2, y2, x3, y3, fill=False):

    ctx = self.ctx
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.line_to(x3, y3)
    ctx.close_path()

    if fill:
      ctx.fill()
    else:
      ctx.stroke()

  def random_parallelogram(self, x1, y1, x2, y2, x3, y3, grains):

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    v1 = array((x2-x1, y2-y1))
    v2 = array((x3-x1, y3-y1))

    a1 = random((grains, 1))
    a2 = random((grains, 1))

    dd = v1*a1 + v2*a2

    dd[:, 0] += x1
    dd[:, 1] += y1

    for x, y in dd:
      rectangle(x, y, pix, pix)
      fill()

  def random_triangle(self, x1, y1, x2, y2, x3, y3, grains):

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    v1 = array((x2-x1, y2-y1))
    v2 = array((x3-x1, y3-y1))

    a1 = random((2*grains, 1))
    a2 = random((2*grains, 1))

    mask = ((a1+a2)<1).flatten()

    ## discarding half the grains because i am too tired to figure out how to
    ## map the parallelogram to the triangle

    dd = v1*a1 + v2*a2

    dd[:, 0] += x1
    dd[:, 1] += y1

    for x, y in dd[mask, :]:
      rectangle(x, y, pix, pix)
      fill()

  def random_circle(self, x1, y1, r, grains):
    """
    random points in circle. nonuniform distribution.
    """

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    the = random(grains)*pi*2
    rad = random(grains)*r

    xx = x1 + cos(the)*rad
    yy = y1 + sin(the)*rad

    for x, y in zip(xx, yy):
      rectangle(x, y, pix, pix)
      fill()

  def random_uniform_circle(self, x1, y1, r, grains, dst=0):

    from helpers import darts

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    for x, y in darts(grains, x1, y1, r, dst):
      rectangle(x, y, pix, pix)
      fill()

  def dot(self, x, y):

    ctx = self.ctx
    pix = self.pix
    ctx.rectangle(x, y, pix, pix)
    ctx.fill()

  def circle(self, x, y, r, fill=False):

    ctx = self.ctx

    ctx.arc(x, y, r, 0, TWOPI)
    if fill:
      ctx.fill()
    else:
      ctx.stroke()

  def transparent_pix(self):

    op = self.ctx.get_operator()
    self.ctx.set_operator(OPERATOR_SOURCE)
    self.ctx.set_source_rgba(*[1, 1, 1, 0.95])
    self.dot(1-self.pix, 1.0-self.pix)
    self.ctx.set_operator(op)

  def path(self, xy):

    ctx = self.ctx
    ctx.move_to(*xy[0, :])
    for x in xy:
      ctx.line_to(*x)

    ctx.stroke()

  def closed_path(self, coords, fill=True):

    ctx = self.ctx
    line_to = ctx.line_to

    x, y = coords[0]
    ctx.move_to(x, y)

    for x, y in coords[1:]:
      line_to(x, y)

    ctx.close_path()

    if fill:
      ctx.fill()
    else:
      ctx.stroke()

  def circle_path(self, coords, r, fill=False):

    ctx = self.ctx
    for x, y in coords:
      ctx.arc(x, y, r, 0, TWOPI)
      if fill:
        ctx.fill()
      else:
        ctx.stroke()

  def circles(self, x1, y1, x2, y2, r, nmin=2):

    arc = self.ctx.arc
    fill = self.ctx.fill

    dx = x1-x2
    dy = y1-y2
    dd = sqrt(dx*dx+dy*dy)

    n = int(dd/self.pix)
    n = n if n>nmin else nmin

    a = arctan2(dy, dx)

    scale = linspace(0, dd, n)

    xp = x1-scale*cos(a)
    yp = y1-scale*sin(a)

    for x, y in zip(xp, yp):
      arc(x, y, r, 0, pi*2.)
      fill()

  def sandstroke_orthogonal(self, xys, height=None, steps=10, grains=10):

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    if not height:
      height = pix*10

    dx = xys[:, 2] - xys[:, 0]
    dy = xys[:, 3] - xys[:, 1]

    aa = arctan2(dy, dx)
    directions = column_stack([cos(aa), sin(aa)])
    dd = sqrt(square(dx)+square(dy))

    aa_orth = aa + pi*0.5
    directions_orth = column_stack([cos(aa_orth),sin(aa_orth)])

    for i,d in enumerate(dd):

      xy_start = xys[i,:2] + \
        directions[i,:]*random((steps,1))*d

      for xy in xy_start:
        points = xy + \
          directions_orth[i,:]*random((grains,1))*height
        for x,y in points:
          rectangle(x,y,pix,pix)
          fill()

  def sandstroke_non_linear(self,xys,grains=10,left=True):

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    dx = xys[:,2] - xys[:,0]
    dy = xys[:,3] - xys[:,1]

    aa = arctan2(dy,dx)
    directions = column_stack([cos(aa),sin(aa)])

    dd = sqrt(square(dx)+square(dy))

    for i,d in enumerate(dd):
      rnd = sqrt(random((grains,1)))
      if left:
        rnd = 1.0-rnd

      for x,y in xys[i,:2] + directions[i,:]*rnd*d:
        rectangle(x,y,pix,pix)
        fill()

  def sandstroke(self,xys,grains=10):

    pix = self.pix
    rectangle = self.ctx.rectangle
    fill = self.ctx.fill

    dx = xys[:,2] - xys[:,0]
    dy = xys[:,3] - xys[:,1]

    aa = arctan2(dy,dx)
    directions = column_stack([cos(aa),sin(aa)])

    dd = sqrt(square(dx)+square(dy))

    for i,d in enumerate(dd):
      for x,y in xys[i,:2] + directions[i,:]*random((grains,1))*d:
        rectangle(x,y,pix,pix)
        fill()

  def set_front_from_colors(self, i, a=1):

    ii = i%self.ncolors

    r,g,b = self.colors[ii]
    c = [r,g,b,a]

    self.front = c
    self.ctx.set_source_rgba(*c)

  def get_colors_from_file(self, fn):

    import Image
    from numpy.random import shuffle

    def p(f):
      return float('{:0.5f}'.format(f))

    scale = 1./255.
    im = Image.open(fn)
    w, h = im.size
    rgbim = im.convert('RGB')
    res = []
    for i in range(0, w):
      for j in range(0, h):
        r, g, b = rgbim.getpixel((i, j))
        res.append([p(r*scale), p(g*scale), p(b*scale)])

    shuffle(res)

    self.colors = res
    self.ncolors = len(res)


class Animate(Render):

  def __init__(self, n, front, back, step):

    from gi.repository import Gtk
    from gi.repository import GObject

    Render.__init__(self, n, front, back)

    window = Gtk.Window()
    self.window = window
    window.resize(self.n, self.n)

    self.step = step

    window.connect("destroy", self.__destroy)
    darea = Gtk.DrawingArea()
    # darea.connect("expose-event", self.expose)
    self.darea = darea

    window.add(darea)
    window.show_all()

    #self.cr = self.darea.window.cairo_create()
    self.steps = 0
    GObject.idle_add(self.step_wrap)

  def __destroy(self,*args):

    from gi.repository import Gtk

    Gtk.main_quit(*args)

  def start(self):

    from gi.repository import Gtk

    Gtk.main()

  def expose(self, *args):

    #cr = self.cr
    # cr = self.darea.window.cairo_create()
    cr = self.darea.get_property('window').cairo_create()
    cr.set_source_surface(self.sur, 0, 0)
    cr.paint()

  def step_wrap(self):

    res = self.step(self)
    self.steps += 1
    self.expose()

    return res

