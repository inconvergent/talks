#!/usr/bin/python3
# -*- coding: utf-8 -*-

from numpy import array


BACK = [1, 1, 1, 1]
FRONT = [0, 0, 0, 0.5]

SIZE = 1000
ONE = 1./SIZE
EDGE = 0.05


SCALE = array((0, 1), 'float')*0.01*ONE
NUM = 100



def main():
  from modules.render import Animate
  from modules.walkers import Walkers
  from time import sleep

  walkers = []

  for i in range(1):
    w = Walkers(
        SIZE,
        EDGE,
        SCALE,
        NUM
        ).run()
    walkers.append(w)

  def wrap(render):
    render.clear_canvas()
    for k, w in enumerate(walkers):
      dots = next(w)
      render.path(dots)
    sleep(0.01)
    return True

  render = Animate(SIZE, BACK, FRONT, wrap)
  render.set_line_width(3*ONE)
  render.start()


if __name__ == '__main__':
  main()
