"""
Moduł odpowiedzialny za proceduralne generowanie tekstury cząsteczki.

Tworzy kwadratową teksturę RGBA zawierającą biały, miękko wygaszany
okrąg, który może być wykorzystywany jako sprite pojedynczej kropli
w systemie cząsteczek fontanny.
"""

import math
import numpy as np
from OpenGL.GL import *


def make_sprite_texture(size=64):
    """
    Generuje i tworzy teksturę sprite'a wykorzystywaną przez cząsteczki.

    Tworzy kwadratową tablicę RGBA, w której kanały RGB mają wartość
    białą, natomiast kanał alfa jest wyznaczany na podstawie odległości
    danego piksela od środka tekstury. Środkowa część sprite'a jest
    całkowicie nieprzezroczysta, a przezroczystość stopniowo zwiększa
    się w kierunku krawędzi.

    Gotowe dane są przesyłane do tekstury OpenGL, dla której ustawiane
    jest filtrowanie liniowe oraz blokowanie próbkowania na krawędziach.

    Args:
        size (int): Szerokość i wysokość generowanej tekstury w pikselach.
            Domyślnie 64.

    Returns:
        int: Identyfikator utworzonej tekstury OpenGL.
    """
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