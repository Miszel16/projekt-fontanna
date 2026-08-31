"""
Moduł odpowiedzialny za wczytywanie tekstur z plików graficznych.

Wczytuje obraz za pomocą biblioteki Pygame, konwertuje go do formatu RGBA
i tworzy na jego podstawie teksturę OpenGL. Konfiguruje również sposób
powtarzania tekstury, filtrowanie, mipmapy oraz opcjonalne filtrowanie
anizotropowe.
"""

import pygame
from OpenGL.GL import *


def load_texture(path):
    """
    Wczytuje obraz z pliku i tworzy na jego podstawie teksturę OpenGL.

    Obraz jest ładowany za pomocą Pygame i konwertowany do surowych
    danych RGBA. Następnie tworzony jest obiekt tekstury OpenGL,
    do którego przesyłane są dane obrazu.

    Funkcja ustawia powtarzanie tekstury w obu kierunkach, liniowe
    filtrowanie oraz generuje mipmapy. Jeśli filtrowanie anizotropowe
    jest obsługiwane przez środowisko OpenGL, ustawiana jest jego
    maksymalna dostępna wartość.

    Args:
        path (str): Ścieżka do pliku graficznego zawierającego teksturę.

    Returns:
        int: Identyfikator utworzonej tekstury OpenGL.
    """
    # wczytauje obraz i zamienia na surowe bajty RGBA
    surface = pygame.image.load(path)
    image_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glGenerateMipmap(GL_TEXTURE_2D)

    # Filtrowanie anizotropowe - najskuteczniejsze przeciw migotaniu podlogi
    try:
        from OpenGL.GL.EXT.texture_filter_anisotropic import (
            GL_TEXTURE_MAX_ANISOTROPY_EXT, GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        max_aniso = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_aniso)
    except Exception:
        pass

    return tex