"""
Moduł odpowiedzialny za obsługę materiałów wykorzystywanych podczas renderowania.

Klasa Material tworzy program shaderowy na podstawie wskazanych plików
vertex shadera i fragment shadera oraz umożliwia jego aktywowanie
przed renderowaniem obiektów sceny.
"""


from OpenGL.GL import *
from Utils import create_program


class Material:
    """
    Reprezentuje materiał oparty na programie shaderowym OpenGL.

    Klasa przechowuje identyfikator programu shaderowego utworzonego
    z kodu vertex shadera i fragment shadera oraz umożliwia jego
    aktywację podczas renderowania.
    """


    def __init__(self, vertex_shader, fragment_shader):
        """
        Tworzy program shaderowy na podstawie wskazanych plików shaderów.

        Odczytuje kod vertex shadera i fragment shadera z plików,
        przekazuje ich zawartość do funkcji create_program() i zapisuje
        identyfikator utworzonego programu OpenGL.

        Args:
            vertex_shader (str): Ścieżka do pliku zawierającego kod vertex shadera.
            fragment_shader (str): Ścieżka do pliku zawierającego kod fragment shadera.

        Returns:
            None
        """

        self.program_id = create_program(
            open(vertex_shader).read(),
            open(fragment_shader).read())



    def use(self):
        """
        Aktywuje program shaderowy przypisany do materiału.

        Ustawia program zapisany w program_id jako aktualnie używany
        program shaderowy OpenGL za pomocą funkcji glUseProgram().

        Args:
            Brak.

        Returns:
            None
        """
        glUseProgram(self.program_id)
