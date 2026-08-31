import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform

# Rozmiar podlogi (polowa boku kwadratu) i ile razy powtorzyc teksture.
FLOOR_SIZE = 40.0
TILES = 100.0        # ile razy tekstura powtarza sie na calej podlodze
                    # (wiecej = drobniejsza kostka, mniej = wieksza)


class FloorMesh:
    def __init__(self, material, texture):
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
