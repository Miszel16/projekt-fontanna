"""
SceneMesh.py
Statyczna geometria sceny: niebo, trawa, szara misa fontanny, kolumna
oraz DNO basenu w kolorze wody. Wszystko jako trojkaty z kolorem wierzcholka.

Kazdy wierzcholek: pozycja(vec3) + kolor(vec3), zaladowane przez GraphicsData.
Rysowanie w stylu kursu: glBindVertexArray + glDrawArrays.
"""
import math
import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform
from Settings import COLUMN_HEIGHT, LOWER_BOWL_Y, UPPER_BOWL_Y

# --- KOLORY (mozesz je swobodnie zmieniac) ---------------------------------
SKY = (0.53, 0.81, 0.92)     # niebieskie niebo (jak na obrazku)
GRASS = (0.18, 0.70, 0.28)   # zielona trawa
GRAY = (0.55, 0.55, 0.55)    # szara misa
GRAY_DARK = (0.42, 0.42, 0.42)
# DNO fontanny - niebieskie jak woda. Na szare zmien na np. (0.5, 0.5, 0.5).
WATER = (0.20, 0.55, 0.85)


class SceneMesh:
    def __init__(self, material):
        self.material = material
        positions, colors = self._build()
        self.vertex_count = len(positions)

        self.vao_ref = glGenVertexArrays(1)
        glBindVertexArray(self.vao_ref)

        self.pos_data = GraphicsData("vec3", positions)
        self.pos_data.create_variable(material.program_id, "position")
        self.col_data = GraphicsData("vec3", colors)
        self.col_data.create_variable(material.program_id, "color")

    # ---- budowa geometrii -------------------------------------------------
    def _build(self):
        positions = []
        colors = []

        def quad(p1, p2, p3, p4, col):
            for p in (p1, p2, p3, p1, p3, p4):
                positions.append(p)
                colors.append(col)

        def tri(p1, p2, p3, col):
            for p in (p1, p2, p3):
                positions.append(p)
                colors.append(col)

        # NIEBO - duzy pionowy prostokat w tle
        quad((-40, -2, -20), (40, -2, -20), (40, 40, -20), (-40, 40, -20), SKY)
        # (TRAWA -> FloorMesh; kamien -> FountainMesh; tafle wody -> WaterMesh)

        return (np.array(positions, np.float32),
                np.array(colors, np.float32))

    # ---- rysowanie --------------------------------------------------------
    def draw(self, projection, view):
        self.material.use()
        proj_u = Uniform("mat4", projection)
        proj_u.find_variable(self.material.program_id, "projection_matrix")
        proj_u.load()
        view_u = Uniform("mat4", view)
        view_u.find_variable(self.material.program_id, "view_matrix")
        view_u.load()

        glBindVertexArray(self.vao_ref)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)