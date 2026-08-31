import math
import numpy as np
import pygame
from pygame.locals import *
from Transformations import look_at


class Camera:
    def __init__(self):
        self.angle = math.radians(35)          # kat poziomy wokol fontanny
        self.height = 3.0                      # wysokosc kamery
        self.radius = 9.0                      # odleglosc od srodka
        self.target = np.array([0.0, 1.2, 0.0], np.float32)
        self.VM = np.identity(4, np.float32)
        self._recompute()

    def _recompute(self):
        eye = (math.cos(self.angle) * self.radius,
               self.height,
               math.sin(self.angle) * self.radius)
        self.VM = look_at(eye, self.target, (0.0, 1.0, 0.0))

    def get_VM(self):
        return self.VM

    def update(self, dt):
        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            self.angle += 1.2 * dt
        if key[K_RIGHT]:
            self.angle -= 1.2 * dt
        if key[K_UP]:
            self.height = min(self.height + 3.0 * dt, 9.0)
        if key[K_DOWN]:
            self.height = max(self.height - 3.0 * dt, 0.3)
        if key[K_PLUS] or key[K_KP_PLUS] or key[K_EQUALS]:
            self.radius = max(self.radius - 4.0 * dt, 4.0)
        if key[K_MINUS] or key[K_KP_MINUS]:
            self.radius = min(self.radius + 4.0 * dt, 20.0)
        self._recompute()
