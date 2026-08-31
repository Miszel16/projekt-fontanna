"""
Moduł odpowiedzialny za obsługę danych wierzchołków przesyłanych do OpenGL.

Udostępnia klasę GraphicsData, która tworzy i zarządza buforem VBO,
przesyła dane do pamięci GPU, umożliwia ich dynamiczną aktualizację
oraz łączy bufor z odpowiednim atrybutem programu shaderowego.
"""

import numpy as np
from OpenGL.GL import *


class GraphicsData:
    """
    Reprezentuje bufor danych wierzchołków przechowywany w pamięci GPU.

    Klasa zarządza tworzeniem bufora OpenGL, przesyłaniem i aktualizacją
    danych oraz konfiguracją atrybutów wejściowych vertex shadera.
    """


    def __init__(self, data_type, data, usage=GL_STATIC_DRAW):
        """
        Inicjalizuje bufor danych OpenGL.

        Zapisuje typ oraz dane wejściowe, tworzy nowy obiekt bufora VBO
        i przesyła jego początkową zawartość do pamięci GPU.

        Args:
            data_type (str): Typ pojedynczego elementu danych.
                Obsługiwane wartości to "vec3", "vec2" oraz "float".
            data: Dane, które mają zostać zapisane w buforze.
            usage: Sposób wykorzystania bufora przez OpenGL.
                Domyślnie GL_STATIC_DRAW.

        Returns:
            None
        """
        self.data_type = data_type
        self.data = data
        self.usage = usage
        self.buffer_ref = glGenBuffers(1)
        self.load()



    def load(self):
        """
        Przesyła aktualne dane obiektu do bufora OpenGL.

        Konwertuje dane do tablicy liczb typu float32, wiąże utworzony
        bufor jako GL_ARRAY_BUFFER i zapisuje w nim całą zawartość danych.

        Args:
            Brak.

        Returns:
            None
        """
        data = np.array(self.data, np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_ref)
        glBufferData(GL_ARRAY_BUFFER, data.ravel(), self.usage)




    def update(self, data):
        """
        Aktualizuje zawartość istniejącego bufora OpenGL.

        Zastępuje przechowywane dane nowymi wartościami i aktualizuje
        zawartość istniejącego bufora GPU bez tworzenia nowego obiektu.
        Metoda wykorzystywana jest między innymi dla dynamicznie
        zmieniających się danych cząsteczek.

        Args:
            data: Nowe dane, które mają zostać zapisane w buforze.

        Returns:
            None
        """

        """Podmienia dane w istniejacym buforze (dla animowanych czastek)."""
        self.data = data
        arr = np.array(data, np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_ref)
        glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr.ravel())



    def create_variable(self, program_id, variable_name):
        """
        Łączy bufor danych z atrybutem wejściowym vertex shadera.

        Pobiera lokalizację wskazanego atrybutu z programu shaderowego,
        wiąże odpowiedni bufor i konfiguruje sposób interpretowania danych
        zależnie od typu określonego w data_type. Na końcu aktywuje
        skonfigurowany atrybut wierzchołka.

        Jeśli wskazany atrybut nie istnieje w programie shaderowym,
        funkcja kończy działanie bez wykonywania konfiguracji.

        Args:
            program_id (int): Identyfikator programu shaderowego OpenGL.
            variable_name (str): Nazwa atrybutu wejściowego w vertex shaderze.

        Returns:
            None
        """
        variable_id = glGetAttribLocation(program_id, variable_name)
        if variable_id == -1:
            return
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_ref)
        if self.data_type == "vec3":
            glVertexAttribPointer(variable_id, 3, GL_FLOAT, False, 0, None)
        elif self.data_type == "vec2":
            glVertexAttribPointer(variable_id, 2, GL_FLOAT, False, 0, None)
        elif self.data_type == "float":
            glVertexAttribPointer(variable_id, 1, GL_FLOAT, False, 0, None)
        glEnableVertexAttribArray(variable_id)
