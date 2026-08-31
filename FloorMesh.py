"""
Moduł definiujący geometrię i renderowanie podłogi sceny.

Podłoga jest reprezentowana jako kwadrat zbudowany z dwóch trójkątów
leżących w płaszczyźnie XZ na wysokości y = 0.

Moduł przygotowuje dane wierzchołków i współrzędnych tekstury,
tworzy obiekt VAO oraz przekazuje dane do shaderów podczas renderowania.
Tekstura podłogi jest wielokrotnie powtarzana na całej powierzchni
za pomocą odpowiednio skalowanych współrzędnych UV.
"""


import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform

# Rozmiar podlogi (polowa boku kwadratu) i ile razy powtorzyc teksture.
FLOOR_SIZE = 40.0
TILES = 100.0        # ile razy tekstura powtarza sie na calej podlodze
                    # (wiecej = drobniejsza kostka, mniej = wieksza)



class FloorMesh:
    """
    Reprezentuje teksturowaną podłogę renderowanej sceny.

    Klasa tworzy geometrię kwadratowej powierzchni, przygotowuje
    współrzędne tekstury oraz konfiguruje dane wierzchołków
    wymagane przez program shaderowy.
    """

    def __init__(self, material, texture):
        """
        Inicjalizuje geometrię oraz dane renderowania podłogi.

        Tworzy kwadratową powierzchnię złożoną z dwóch trójkątów,
        generuje współrzędne UV umożliwiające wielokrotne powtarzanie
        tekstury oraz konfiguruje VAO i dane wierzchołków przekazywane
        do programu shaderowego.

        Args:
            material (Material): Materiał zawierający program shaderowy
                używany podczas renderowania podłogi.
            texture: Tekstura przypisana do powierzchni podłogi.

        Returns:
            None
        """

        self.material = material
        self.texture = texture

        s = FLOOR_SIZE
        t = TILES
        # dwa trojkaty tworzace kwadratowa podloge na wysokosci y=0
        positions = [
            (-s, 0, -s), (s, 0, -s), (s, 0, s),
            (-s, 0, -s), (s, 0, s), (-s, 0, s),
        ]
        # wspolrzedne UV 0..t (t=powtorzenia) - to daje kafelkowanie
        uvs = [
            (0, 0), (t, 0), (t, t),
            (0, 0), (t, t), (0, t),
        ]
        self.vertex_count = len(positions)

        self.vao_ref = glGenVertexArrays(1)
        glBindVertexArray(self.vao_ref)
        self.pos_data = GraphicsData("vec3", np.array(positions, np.float32))
        self.pos_data.create_variable(material.program_id, "position")
        self.uv_data = GraphicsData("vec2", np.array(uvs, np.float32))
        self.uv_data.create_variable(material.program_id, "uv")



    def draw(self, projection, view):
        """
        Renderuje podłogę przy użyciu aktualnych macierzy projekcji i widoku.

        Aktywuje materiał podłogi, przekazuje do shaderów macierz projekcji,
        macierz widoku oraz teksturę, a następnie renderuje przygotowaną
        geometrię jako zbiór trójkątów.

        Args:
            projection (numpy.ndarray): Macierz projekcji 4x4 używana
                do transformacji sceny.
            view (numpy.ndarray): Macierz widoku 4x4 określająca
                położenie i orientację kamery.

        Returns:
            None
        """

        self.material.use()
        proj_u = Uniform("mat4", projection)
        proj_u.find_variable(self.material.program_id, "projection_matrix")
        proj_u.load()
        view_u = Uniform("mat4", view)
        view_u.find_variable(self.material.program_id, "view_matrix")
        view_u.load()
        tex_u = Uniform("sampler2D", (self.texture, 0))
        tex_u.find_variable(self.material.program_id, "floor_texture")
        tex_u.load()

        glBindVertexArray(self.vao_ref)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
