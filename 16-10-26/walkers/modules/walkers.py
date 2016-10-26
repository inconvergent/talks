#!/usr/bin/python3

from numpy.random import random
from numpy import ones
from numpy import zeros
from numpy import cumsum
from numpy import column_stack
from numpy import linspace

class Walkers():
  def __init__(self, size, edge, scale, num):

    self.size = size
    self.edge = edge
    self.n = num
    self.one = 1.0/size

    self.scale = scale

    x = linspace(edge, 1.0-edge, self.n)
    y = ones(self.n, 'float')*0.5
    self._walkers = column_stack((x, y))
    self._speed = zeros((self.n, 2), 'float')

  def run(self):
    while True:
      dd = column_stack((
          1.0-2.0*random(self.n),
          1.0-2.0*random(self.n)
          ))*self.scale

      self._speed += dd
      self._walkers += self._speed

      yield self._walkers

  def run2(self):
    while True:
      dd = column_stack((
          1.0-2.0*random(self.n),
          1.0-2.0*random(self.n)
          ))*self.scale

      self._speed += dd
      self._walkers += cumsum(self._speed, axis=0)

      yield self._walkers

class BadWalkers():
  def __init__(self, size, edge, scale, num):

    self.size = size
    self.edge = edge
    self.n = num
    self.one = 1.0/size

    self.scale = scale

    x = linspace(edge, 1.0-edge, self.n)
    y = ones(self.n, 'float')*0.5
    self._walkers = column_stack((x, y))
    self._speed = zeros((self.n, 2), 'float')

  def run(self):
    while True:
      self._walkers[:, 1] = 0.5 + (1.0-2.0*random(self.n))*self.scale[1]
      yield self._walkers

  def run2(self):
    while True:
      self._walkers[:, 1] += (1.0-2.0*random(self.n))*self.scale[1]
      yield self._walkers

