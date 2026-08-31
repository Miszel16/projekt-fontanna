"""
Moduł odpowiedzialny za generowanie i renderowanie powierzchni wody fontanny.

Tworzy teksturowane, poziome powierzchnie wody dla głównego basenu
oraz dwóch talerzy fontanny. Geometria każdej tafli generowana jest
w postaci koła złożonego z trójkątów rozmieszczonych wokół wspólnego środka.
"""

import math
import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform
from Settings import LOWER_BOWL_Y, UPPER_BOWL_Y

TILES = 1.0    # ile razy tekstura wody pokrywa tafle basenu (1 = raz na cala)


class WaterMesh:
    """
    Reprezentuje powierzchnie wody znajdujące się w elementach fontanny.

    Klasa generuje geometrię tafli wody, przygotowuje współrzędne UV
    oraz konfiguruje dane wymagane do ich renderowania w OpenGL.
    """


    def __init__(self, material, texture):
        """
        Inicjalizuje geometrię i dane renderowania powierzchni wody.

        Generuje wierzchołki oraz współrzędne UV wszystkich tafli wody,
        tworzy obiekt VAO i przygotowuje bufory przechowujące pozycje
        oraz współrzędne tekstury.

        Args:
            material (Material): Materiał zawierający program shaderowy
                używany do renderowania powierzchni wody.
            texture: Tekstura nakładana na powierzchnie wody.

        Returns:
            None
        """
        self.material = material
        self.texture = texture
        positions, uvs = self._build()
        self.vertex_count = len(positions)

        self.vao_ref = glGenVertexArrays(1)
        glBindVertexArray(self.vao_ref)
        self.pos_data = GraphicsData("vec3", positions)
        self.pos_data.create_variable(material.program_id, "position")
        self.uv_data = GraphicsData("vec2", uvs)
        self.uv_data.create_variable(material.program_id, "uv")



    def _build(self):
        """
        Generuje geometrię wszystkich powierzchni wody fontanny.

        Tworzy okrągłe tafle wody dla głównego basenu oraz dwóch
        talerzy fontanny. Każda powierzchnia składa się z trójkątów
        rozmieszczonych promieniście wokół środka.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]:
                Tablica pozycji wierzchołków oraz odpowiadająca jej
                tablica współrzędnych UV.
        """
        positions = []
        uvs = []
        seg = 10          # tyle samo co reszta


        def disc(radius, y, tiles):
            """
            Generuje pojedynczą okrągłą powierzchnię wody.

            Dzieli koło na segmenty i dla każdego z nich tworzy trójkąt
            złożony ze środka powierzchni oraz dwóch kolejnych punktów
            znajdujących się na jej obwodzie.

            Args:
                radius (float): Promień generowanej powierzchni.
                y (float): Wysokość powierzchni w osi Y.
                tiles (float): Skala współrzędnych UV określająca sposób
                    rozmieszczenia tekstury na powierzchni.

            Returns:
                None
            """
            for i in range(seg):
                a0 = 2 * math.pi * i / seg
                a1 = 2 * math.pi * (i + 1) / seg
                p_c = (0.0, y, 0.0)
                p0 = (radius * math.cos(a0), y, radius * math.sin(a0))
                p1 = (radius * math.cos(a1), y, radius * math.sin(a1))
                # UV z pozycji xz: srodek=0.5,0.5; brzeg wg kata


                def uv_of(x, z):
                    """
                    Wyznacza współrzędne UV dla punktu powierzchni wody.

                    Przelicza współrzędne X i Z wierzchołka na współrzędne
                    tekstury względem środka koła i jego promienia.

                    Args:
                        x (float): Współrzędna X wierzchołka.
                        z (float): Współrzędna Z wierzchołka.

                    Returns:
                        tuple[float, float]: Współrzędne tekstury (u, v).
                    """
                    return (0.5 + 0.5 * tiles * x / radius,
                            0.5 + 0.5 * tiles * z / radius)
                positions.extend([p_c, p0, p1])
                uvs.extend([(0.5, 0.5), uv_of(p0[0], p0[2]), uv_of(p1[0], p1[2])])

        # basen (duza tafla) + talerze (male tafle)
        r_in = 2.6
        h = 0.5
        disc(r_in, h * 0.4, TILES)
        disc(1.5 - 0.25, LOWER_BOWL_Y + 0.28 * 0.5, TILES)
        disc(1.0 - 0.25, UPPER_BOWL_Y + 0.28 * 0.5, TILES)

        return (np.array(positions, np.float32),
                np.array(uvs, np.float32))



    def draw(self, projection, view):
        """
        Renderuje wszystkie powierzchnie wody fontanny.

        Aktywuje materiał, przekazuje do programu shaderowego macierz
        projekcji, macierz widoku oraz teksturę, a następnie renderuje
        przygotowaną geometrię jako trójkąty OpenGL.

        Args:
            projection (numpy.ndarray): Macierz projekcji 4x4.
            view (numpy.ndarray): Macierz widoku 4x4 kamery.

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