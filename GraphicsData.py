import numpy as np
from OpenGL.GL import *


class GraphicsData:
    def __init__(self, data_type, data, usage=GL_STATIC_DRAW):
        self.data_type = data_type
        self.data = data
        self.usage = usage
        self.buffer_ref = glGenBuffers(1)
        self.load()

    def load(self):
        data = np.array(self.data, np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_ref)
        glBufferData(GL_ARRAY_BUFFER, data.ravel(), self.usage)

    def update(self, data):
        """Podmienia dane w istniejacym buforze (dla animowanych czastek)."""
        self.data = data
        arr = np.array(data, np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_ref)
        glBufferSubData(GL_ARRAY_BUFFER, 0, arr.nbytes, arr.ravel())

    def create_variable(self, program_id, variable_name):
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
