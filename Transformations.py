"""
Moduł zawierający funkcje pomocnicze do tworzenia podstawowych
macierzy transformacji wykorzystywanych podczas renderowania 3D.

Udostępnia funkcje tworzące macierz jednostkową, macierz projekcji
perspektywicznej oraz macierz widoku kamery.
"""
import math
import numpy as np


def identity():
    """
    Tworzy macierz jednostkową 4x4.

    Macierz jednostkowa nie wprowadza żadnej transformacji
    i może być używana jako początkowa macierz transformacji.

    Args:
        Brak.

    Returns:
        numpy.ndarray: Macierz jednostkowa 4x4 typu float32.
    """
    return np.identity(4, np.float32)


def perspective_matrix(fovy_deg, aspect, near, far):
    """
    Tworzy macierz projekcji perspektywicznej.

    Macierz odwzorowuje scenę 3D na przestrzeń widoku z uwzględnieniem
    perspektywy. Obiekty znajdujące się dalej od kamery są dzięki temu
    renderowane jako mniejsze.

    Args:
        fovy_deg (float): Pionowy kąt widzenia kamery w stopniach.
        aspect (float): Proporcja szerokości obrazu do jego wysokości.
        near (float): Odległość bliskiej płaszczyzny obcinania.
        far (float): Odległość dalekiej płaszczyzny obcinania.

    Returns:
        numpy.ndarray: Macierz projekcji perspektywicznej 4x4
            typu float32.
    """
    # Macierz rzutowania perspektywicznego
    f = 1.0 / math.tan(math.radians(fovy_deg) / 2.0)
    m = np.zeros((4, 4), np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def look_at(eye, center, up):
    """
    Tworzy macierz widoku określającą położenie i orientację kamery.

    Na podstawie pozycji kamery, punktu obserwowanego oraz wektora
    kierunku góry wyznacza lokalne osie kamery, a następnie buduje
    macierz widoku transformującą współrzędne świata do przestrzeni
    kamery.

    Args:
        eye: Pozycja kamery w przestrzeni 3D jako [x, y, z].
        center: Punkt w przestrzeni 3D, w kierunku którego patrzy kamera.
        up: Wektor określający kierunek góry kamery.

    Returns:
        numpy.ndarray: Macierz widoku 4x4 typu float32.
    """
    # Macierz widoku - kamera w 'eye' patrzy na 'center'
    eye = np.array(eye, np.float32)
    center = np.array(center, np.float32)
    up = np.array(up, np.float32)

    f = center - eye
    f = f / np.linalg.norm(f)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)

    m = np.identity(4, np.float32)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m
