"""
Moduł odpowiedzialny za obsługę zmiennych typu uniform w shaderach OpenGL.

Klasa Uniform przechowuje wartość oraz typ zmiennej uniform, wyszukuje
jej lokalizację w programie shaderowym i przesyła odpowiednie dane do GPU.
Obsługiwane są między innymi wektory, liczby zmiennoprzecinkowe,
macierze oraz tekstury 2D.
"""
from OpenGL.GL import *


class Uniform:
    """
    Reprezentuje pojedynczą zmienną uniform programu shaderowego.

    Klasa przechowuje typ i wartość zmiennej, jej lokalizację
    w programie OpenGL oraz umożliwia przesłanie danych do shadera.
    """

    def __init__(self, data_type, data):
        """
        Inicjalizuje obiekt reprezentujący zmienną uniform.

        Zapisuje typ oraz wartość zmiennej. Identyfikator lokalizacji
        uniformu jest początkowo niezdefiniowany i zostaje ustawiony
        później przez metodę find_variable().

        Args:
            data_type (str): Typ danych uniformu, np. "vec3", "float",
                "mat4" lub "sampler2D".
            data: Wartość, która ma zostać przekazana do shadera.

        Returns:
            None
        """
        self.data_type = data_type
        self.data = data
        self.variable_id = None



    def find_variable(self, program_id, variable_name):
        """
        Wyszukuje lokalizację zmiennej uniform w programie shaderowym.

        Pobiera identyfikator lokalizacji wskazanej zmiennej za pomocą
        glGetUniformLocation() i zapisuje go w obiekcie.

        Args:
            program_id (int): Identyfikator programu shaderowego OpenGL.
            variable_name (str): Nazwa zmiennej uniform zdefiniowanej
                w kodzie shadera.

        Returns:
            None
        """
        self.variable_id = glGetUniformLocation(program_id, variable_name)



    def load(self):
        """
        Przesyła przechowywaną wartość do zmiennej uniform w shaderze.

        W zależności od wartości data_type wybierana jest odpowiednia
        funkcja OpenGL do przesłania danych. Obsługiwane są typy vec3,
        float, mat4 oraz sampler2D.

        Dla tekstury sampler2D funkcja dodatkowo aktywuje wskazaną
        jednostkę teksturującą i wiąże z nią odpowiedni obiekt tekstury.

        Args:
            Brak.

        Returns:
            None
        """
        if self.data_type == "vec3":
            glUniform3f(self.variable_id,
                        self.data[0], self.data[1], self.data[2])
        elif self.data_type == "float":
            glUniform1f(self.variable_id, self.data)
        elif self.data_type == "mat4":
            glUniformMatrix4fv(self.variable_id, 1, GL_TRUE, self.data)
        elif self.data_type == "sampler2D":
            texture_obj, texture_unit = self.data
            glActiveTexture(GL_TEXTURE0 + texture_unit)
            glBindTexture(GL_TEXTURE_2D, texture_obj)
            glUniform1i(self.variable_id, texture_unit)
