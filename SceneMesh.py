"""
Moduł odpowiedzialny za generowanie i renderowanie statycznej geometrii sceny.

Geometria przechowywana jest jako zestaw trójkątów, których każdy
wierzchołek posiada pozycję 3D oraz przypisany kolor. Dane są
przekazywane do GPU za pomocą klasy GraphicsData.
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
    """
    Reprezentuje statyczną geometrię sceny.

    Klasa generuje pozycje i kolory wierzchołków, przygotowuje
    odpowiednie bufory OpenGL oraz odpowiada za renderowanie
    statycznych elementów sceny.
    """

    def __init__(self, material):
        """
        Inicjalizuje geometrię oraz dane renderowania sceny.

        Generuje geometrię sceny, tworzy obiekt VAO oraz przygotowuje
        bufory zawierające pozycje i kolory wierzchołków.

        Args:
            material (Material): Materiał zawierający program shaderowy
                używany do renderowania sceny.

        Returns:
            None
        """
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
        """
        Generuje statyczną geometrię sceny.

        Tworzy listy pozycji i kolorów wierzchołków, wykorzystując
        pomocnicze funkcje do generowania trójkątów i czworokątów.
        W aktualnej wersji funkcja tworzy prostokąt reprezentujący
        tło nieba.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]:
                Tablica pozycji wierzchołków oraz odpowiadająca jej
                tablica kolorów RGB.
        """
        positions = []
        colors = []



        def quad(p1, p2, p3, p4, col):
            """
            Dodaje czworokąt do generowanej geometrii sceny.

            Czworokąt zdefiniowany przez cztery punkty dzielony jest
            na dwa trójkąty. Każdemu utworzonemu wierzchołkowi
            przypisywany jest ten sam kolor.

            Args:
                p1: Pierwszy wierzchołek czworokąta.
                p2: Drugi wierzchołek czworokąta.
                p3: Trzeci wierzchołek czworokąta.
                p4: Czwarty wierzchołek czworokąta.
                col: Kolor RGB przypisany do wierzchołków.

            Returns:
                None
            """
            for p in (p1, p2, p3, p1, p3, p4):
                positions.append(p)
                colors.append(col)



        def tri(p1, p2, p3, col):
            """
            Dodaje pojedynczy trójkąt do generowanej geometrii sceny.

            Zapisuje trzy przekazane wierzchołki oraz przypisuje
            każdemu z nich wskazany kolor RGB.

            Args:
                p1: Pierwszy wierzchołek trójkąta.
                p2: Drugi wierzchołek trójkąta.
                p3: Trzeci wierzchołek trójkąta.
                col: Kolor RGB przypisany do wierzchołków.

            Returns:
                None
            """
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
        """
        Renderuje statyczną geometrię sceny.

        Aktywuje przypisany materiał, przekazuje do shaderów
        macierz projekcji oraz macierz widoku, a następnie
        renderuje przygotowane wierzchołki jako trójkąty OpenGL.

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

        glBindVertexArray(self.vao_ref)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)