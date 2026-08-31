"""
Moduł obsługujący kamerę orbitalną sceny.

Kamera porusza się wokół środka sceny po okręgu o regulowanym promieniu (strzałki).
Użytkownik może zmieniać jej kąt położenia, wysokość oraz odległość (+/-)
od fontanny za pomocą klawiatury.

Na podstawie aktualnego położenia kamery wyznaczana jest macierz widoku,
wykorzystywana podczas renderowania sceny.
"""


import math
import numpy as np
import pygame
from pygame.locals import *
from Transformations import look_at


"""
Reprezentuje kamerę orbitalną poruszającą się wokół środka sceny.

Położenie kamery określane jest za pomocą kąta obrotu, wysokości
oraz promienia względem punktu obserwowanego. Klasa odpowiada
również za obsługę sterowania kamerą i aktualizację macierzy widoku.
"""
class Camera:
    def __init__(self):
        """
        Inicjalizuje kamerę i ustawia jej początkowe parametry.

        Ustawia początkowy kąt kamery, wysokość, odległość od środka
        sceny oraz punkt, w który skierowana jest kamera. Następnie
        wyznacza początkową macierz widoku.

        Args:
            Brak.

        Returns:
            None
        """
        self.angle = math.radians(35)          # kat poziomy wokol fontanny
        self.height = 3.0                      # wysokosc kamery
        self.radius = 9.0                      # odleglosc od srodka
        self.target = np.array([0.0, 1.2, 0.0], np.float32)
        self.VM = np.identity(4, np.float32)
        self._recompute()



    def _recompute(self):
        """
        Ponownie wyznacza położenie kamery oraz jej macierz widoku.

        Pozycja kamery obliczana jest na podstawie aktualnego kąta,
        promienia oraz wysokości. Następnie funkcja look_at() tworzy
        macierz widoku skierowaną z pozycji kamery na punkt target.

        Args:
            Brak.

        Returns:
            None
        """
        eye = (math.cos(self.angle) * self.radius,
               self.height,
               math.sin(self.angle) * self.radius)
        self.VM = look_at(eye, self.target, (0.0, 1.0, 0.0))



    def get_VM(self):
        """
        Zwraca aktualną macierz widoku kamery.
        Returns:
            numpy.ndarray: Macierz widoku kamery 4x4.
        """
        return self.VM



    def update(self, dt):
        """
        Aktualizuje parametry kamery na podstawie wejścia z klawiatury.

        Obsługuje obrót kamery wokół sceny, zmianę jej wysokości oraz
        zmianę odległości od środka. Po przetworzeniu wejścia ponownie
        wyznacza macierz widoku.

        Args:
            dt (float): Czas od poprzedniej klatki wyrażony w sekundach.

        Returns:
            None
        """
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
