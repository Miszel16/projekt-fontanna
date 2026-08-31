"""
Moduł odpowiedzialny za generowanie i renderowanie geometrii fontanny.

Model fontanny tworzony jest programowo z prostych elementów geometrycznych.
Moduł generuje pozycje wierzchołków oraz współrzędne UV dla poszczególnych
części fontanny, a następnie przygotowuje dane do renderowania w OpenGL.
"""

import math
import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform
from Settings import COLUMN_HEIGHT, LOWER_BOWL_Y, UPPER_BOWL_Y

TILES_U = 6.0    # ile razy tekstura owija sie wokol obwodu
TILES_V = 2.0    # ile razy powtarza sie w pionie



class FountainMesh:
    """
    Reprezentuje statyczny model geometryczny fontanny.

    Klasa odpowiada za wygenerowanie geometrii fontanny,
    przygotowanie danych wierzchołków i współrzędnych UV
    oraz renderowanie modelu przy użyciu OpenGL.
    """


    def __init__(self, material, texture):
        """
        Inicjalizuje model geometryczny fontanny.

        Generuje geometrię modelu, zapisuje materiał i teksturę
        oraz przygotowuje VAO i bufory danych zawierające pozycje
        wierzchołków i współrzędne UV.

        Args:
                material (Material): Materiał zawierający program shaderowy
                używany do renderowania fontanny.
                texture: Tekstura nakładana na powierzchnię modelu.

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
        Generuje geometrię wszystkich elementów modelu fontanny.

        Tworzy wierzchołki i współrzędne UV dla dolnego basenu,
        dwóch talerzy oraz centralnego słupa. Powierzchnie modelu
        budowane są z trójkątów rozmieszczonych wokół osi Y.

        Returns:
                tuple[numpy.ndarray, numpy.ndarray]:
                Tablica pozycji wierzchołków oraz odpowiadająca jej
                tablica współrzędnych UV.
        """

        positions = []
        uvs = []

        def quad_uv(p1, p2, p3, p4, u0, u1, v0, v1):
            """
            Dodaje teksturowany czworokąt do generowanej geometrii.
    
            Czworokąt zdefiniowany przez cztery punkty dzielony jest
            na dwa trójkąty. Do każdego wierzchołka przypisywane są
            odpowiednie współrzędne UV.

            Args:
                    p1: Pierwszy wierzchołek czworokąta.
                    p2: Drugi wierzchołek czworokąta.
                    p3: Trzeci wierzchołek czworokąta.
                    p4: Czwarty wierzchołek czworokąta.
                    u0 (float): Początkowa współrzędna U tekstury.
                    u1 (float): Końcowa współrzędna U tekstury.
                    v0 (float): Początkowa współrzędna V tekstury.
                    v1 (float): Końcowa współrzędna V tekstury.

            Returns:
                    None
            """

            data = [(p1, (u0, v0)), (p2, (u1, v0)), (p3, (u1, v1)),
                    (p1, (u0, v0)), (p3, (u1, v1)), (p4, (u0, v1))]
            for p, uv in data:
                positions.append(p)
                uvs.append(uv)

        seg = 10          # tyle samo co w SceneMesh (kanciaste kolo)
        r_out, r_in = 3.2, 2.6
        h = 0.5

        # ---- BASEN (dolna misa): pierscien + sciany ----------
        for i in range(seg):
            a0 = 2 * math.pi * i / seg
            a1 = 2 * math.pi * (i + 1) / seg
            u0 = TILES_U * i / seg
            u1 = TILES_U * (i + 1) / seg
            xo0, zo0 = r_out * math.cos(a0), r_out * math.sin(a0)
            xo1, zo1 = r_out * math.cos(a1), r_out * math.sin(a1)
            xi0, zi0 = r_in * math.cos(a0), r_in * math.sin(a0)
            xi1, zi1 = r_in * math.cos(a1), r_in * math.sin(a1)
            # gorny pierscien (krawedz) - u wzdluz obwodu, v w poprzek pierscienia
            quad_uv((xo0, h, zo0), (xo1, h, zo1), (xi1, h, zi1), (xi0, h, zi0),
                    u0, u1, 0.0, 1.0)
            # sciana zewnetrzna (obie strony)
            quad_uv((xo0, 0, zo0), (xo1, 0, zo1), (xo1, h, zo1), (xo0, h, zo0),
                    u0, u1, 0.0, 1.0)
            quad_uv((xo0, h, zo0), (xo1, h, zo1), (xo1, 0, zo1), (xo0, 0, zo0),
                    u0, u1, 1.0, 0.0)
            # sciana wewnetrzna (obie strony)
            quad_uv((xi0, 0, zi0), (xi1, 0, zi1), (xi1, h, zi1), (xi0, h, zi0),
                    u0, u1, 0.0, 1.0)
            quad_uv((xi0, h, zi0), (xi1, h, zi1), (xi1, 0, zi1), (xi0, 0, zi0),
                    u0, u1, 1.0, 0.0)

        # ---- TALERZE na slupie --------------------------------------------

        def bowl(r_out_b, base_y, tw=0.25, th=0.28):
            """
            Generuje geometrię pojedynczego talerza fontanny.

            Talerz tworzony jest z segmentów rozmieszczonych wokół osi Y.
            Funkcja generuje jego powierzchnie oraz ściany i dodaje
            odpowiadające im współrzędne UV.

            Args:
                    r_out_b (float): Zewnętrzny promień talerza.
                    base_y (float): Położenie podstawy talerza w osi Y.
                    tw (float): Grubość pierścienia talerza.
                    th (float): Wysokość ściany talerza.

            Returns:
                    None
            """

            r_in_b = r_out_b - tw
            for i in range(seg):
                a0 = 2 * math.pi * i / seg
                a1 = 2 * math.pi * (i + 1) / seg
                u0 = TILES_U * i / seg
                u1 = TILES_U * (i + 1) / seg
                xo0, zo0 = r_out_b * math.cos(a0), r_out_b * math.sin(a0)
                xo1, zo1 = r_out_b * math.cos(a1), r_out_b * math.sin(a1)
                xi0, zi0 = r_in_b * math.cos(a0), r_in_b * math.sin(a0)
                xi1, zi1 = r_in_b * math.cos(a1), r_in_b * math.sin(a1)
                top = base_y + th
                # spod talerza (trojkat -> jako cienki quad z u,v)
                positions.extend([(0, base_y, 0), (xo1, base_y, zo1),
                                  (xo0, base_y, zo0)])
                uvs.extend([(0.5, 0.5), (u1, 0.0), (u0, 0.0)])
                # gorny pierscien
                quad_uv((xo0, top, zo0), (xo1, top, zo1),
                        (xi1, top, zi1), (xi0, top, zi0), u0, u1, 0.0, 1.0)
                # sciana zewnetrzna (obie strony)
                quad_uv((xo0, base_y, zo0), (xo1, base_y, zo1),
                        (xo1, top, zo1), (xo0, top, zo0), u0, u1, 0.0, 1.0)
                quad_uv((xo0, top, zo0), (xo1, top, zo1),
                        (xo1, base_y, zo1), (xo0, base_y, zo0), u0, u1, 1.0, 0.0)
                # sciana wewnetrzna (obie strony)
                quad_uv((xi0, base_y, zi0), (xi1, base_y, zi1),
                        (xi1, top, zi1), (xi0, top, zi0), u0, u1, 0.0, 1.0)
                quad_uv((xi0, top, zi0), (xi1, top, zi1),
                        (xi1, base_y, zi1), (xi0, base_y, zi0), u0, u1, 1.0, 0.0)

        bowl(r_out_b=1.5, base_y=LOWER_BOWL_Y)
        bowl(r_out_b=1.0, base_y=UPPER_BOWL_Y)

        # ---- SLUP-STOZEK ---------------------------------------------------
        cr_bottom = 0.55
        cr_top = 0.15
        ch = COLUMN_HEIGHT
        for i in range(seg):
            a0 = 2 * math.pi * i / seg
            a1 = 2 * math.pi * (i + 1) / seg
            u0 = TILES_U * i / seg
            u1 = TILES_U * (i + 1) / seg
            xb0, zb0 = cr_bottom * math.cos(a0), cr_bottom * math.sin(a0)
            xb1, zb1 = cr_bottom * math.cos(a1), cr_bottom * math.sin(a1)
            xt0, zt0 = cr_top * math.cos(a0), cr_top * math.sin(a0)
            xt1, zt1 = cr_top * math.cos(a1), cr_top * math.sin(a1)
            quad_uv((xb0, 0, zb0), (xb1, 0, zb1),
                    (xt1, ch, zt1), (xt0, ch, zt0), u0, u1, 0.0, TILES_V)

        return (np.array(positions, np.float32),
                np.array(uvs, np.float32))



    def draw(self, projection, view):
        """
        Renderuje model fontanny.
        
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
