"""
Moduł zawierający funkcje pomocnicze do obsługi shaderów OpenGL.

Odpowiada za kompilowanie pojedynczych shaderów oraz tworzenie kompletnego
programu shaderowego poprzez połączenie vertex shadera i fragment shadera.
W przypadku błędów kompilacji lub linkowania zgłaszany jest wyjątek
z komunikatem zwróconym przez OpenGL.
"""
from OpenGL.GL import *


def compile_shader(shader_type, shader_source):
    """
    Kompiluje pojedynczy shader OpenGL.

    Tworzy obiekt shadera wskazanego typu, przypisuje do niego kod źródłowy
    i uruchamia proces kompilacji. Następnie sprawdza jej wynik.
    W przypadku błędu usuwa utworzony shader i zgłasza wyjątek
    zawierający komunikat diagnostyczny OpenGL.

    Args:
        shader_type (int): Typ kompilowanego shadera, np.
            GL_VERTEX_SHADER lub GL_FRAGMENT_SHADER.
        shader_source (str): Kod źródłowy shadera w języku GLSL.

    Returns:
        int: Identyfikator poprawnie skompilowanego shadera OpenGL.
    """

    shader_id = glCreateShader(shader_type)
    glShaderSource(shader_id, shader_source)
    glCompileShader(shader_id)
    compile_success = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
    if not compile_success:
        error_message = glGetShaderInfoLog(shader_id)
        glDeleteShader(shader_id)
        error_message = "\n" + error_message.decode("utf-8")
        raise Exception(error_message)
    return shader_id



def create_program(vertex_shader_code, fragment_shader_code):
    """
    Tworzy kompletny program shaderowy OpenGL.

    Kompiluje vertex shader i fragment shader, tworzy nowy program OpenGL,
    dołącza do niego oba shadery i wykonuje ich linkowanie. Po sprawdzeniu
    poprawności linkowania usuwa pojedyncze obiekty shaderów, pozostawiając
    gotowy program shaderowy.

    Args:
        vertex_shader_code (str): Kod źródłowy vertex shadera w języku GLSL.
        fragment_shader_code (str): Kod źródłowy fragment shadera w języku GLSL.

    Returns:
        int: Identyfikator poprawnie utworzonego programu shaderowego OpenGL.

    Raises:
        RuntimeError: Jeśli linkowanie programu shaderowego zakończy się błędem.
    """

    vertex_shader_id = compile_shader(GL_VERTEX_SHADER, vertex_shader_code)
    fragment_shader_id = compile_shader(GL_FRAGMENT_SHADER, fragment_shader_code)

    program_id = glCreateProgram()
    glAttachShader(program_id, vertex_shader_id)
    glAttachShader(program_id, fragment_shader_id)
    glLinkProgram(program_id)

    link_success = glGetProgramiv(program_id, GL_LINK_STATUS)
    if not link_success:
        info = glGetProgramInfoLog(program_id)
        raise RuntimeError(info)

    glDeleteShader(vertex_shader_id)
    glDeleteShader(fragment_shader_id)
    return program_id
