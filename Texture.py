import math
import numpy as np
from OpenGL.GL import *


def make_sprite_texture(size=64):
    data = np.zeros((size, size, 4), np.float32)
    cx = cy = (size - 1) / 2.0
    r = size / 2.0
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / r
            # Lekkie rozmycie
            if d <= 0.55:
                a = 1.0                            # srodek - pelne krycie
            else:
                a = max(0.0, (1.0 - d) / 0.45)     # miekkie zejscie do krawedzi
                a = a * a                          # lagodniejszy gradient
            data[y, x] = (1.0, 1.0, 1.0, a)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0,
                 GL_RGBA, GL_FLOAT, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return tex