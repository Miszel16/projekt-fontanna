import math
import random
import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform
from Settings import EMIT_HEIGHT   # wysokosc tryskania - wspolna z SceneMesh

MAX_PARTICLES = 1200        # maksymalna liczba kropli (minimalistyczny strumien)
SPAWN_PER_FRAME = 14        # ile nowych kropli rodzi sie na klatke
GRAVITY = -9.8             # przyspieszenie grawitacyjne
PARTICLE_LIFETIME = 2.4     # czas zycia kropli (s)

# --- PALETA KOLOROW KROPLI ---------------------------------------------------------
DROP_COLORS = [
    (1.00, 1.00, 1.00),   # bialy
    (0.80, 0.92, 1.00),   # bardzo jasny blekit
    (0.60, 0.82, 1.00),   # jasnoniebieski
    (0.45, 0.72, 0.98),   # niebieski
]

# --- PULSOWANIE ------------------------------------------------------------
# True  = woda tryska cyklicznie (leci chwile, potem pauza - widac przerwy)
# False = woda leci ciagle bez przerwy
PULSE = False
PULSE_ON = 1.3              # ile sekund woda leci
PULSE_OFF = 1.6            # ile sekund przerwy


class Fountain:
    def __init__(self, material, sprite_texture):
        self.material = material
        self.sprite_texture = sprite_texture

        self.pos = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.vel = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.life = np.zeros(MAX_PARTICLES, np.float32)
        self.col = np.zeros((MAX_PARTICLES, 3), np.float32)   # kolor kropli
        self.alive = np.zeros(MAX_PARTICLES, bool)
        self.next_idx = 0
        self.pulse_timer = 0.0     # zegar do sterowania pulsowaniem

        self.gpu_pos = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.gpu_life = np.zeros(MAX_PARTICLES, np.float32)
        self.gpu_col = np.zeros((MAX_PARTICLES, 3), np.float32)

        self.vao_ref = glGenVertexArrays(1)
        glBindVertexArray(self.vao_ref)
        self.pos_data = GraphicsData("vec3", self.gpu_pos, GL_DYNAMIC_DRAW)
        self.pos_data.create_variable(material.program_id, "position")
        self.life_data = GraphicsData("float", self.gpu_life, GL_DYNAMIC_DRAW)
        self.life_data.create_variable(material.program_id, "life")
        self.col_data = GraphicsData("vec3", self.gpu_col, GL_DYNAMIC_DRAW)
        self.col_data.create_variable(material.program_id, "color")

    # ---- Nowe krople -----------------------------------------
    def spawn(self, n):
        for _ in range(n):
            i = self.next_idx
            self.next_idx = (self.next_idx + 1) % MAX_PARTICLES
            angle = random.uniform(0, 2 * math.pi)
            # szerszy rozrzut w bok = krople nie tlocza sie w jednym strumieniu
            spread = random.uniform(0.3, 1.3)
            up = random.uniform(5.0, 5.6)
            vx = math.cos(angle) * spread
            vz = math.sin(angle) * spread

            t = random.uniform(0.0, PARTICLE_LIFETIME)
            self.pos[i] = (vx * t,
                           EMIT_HEIGHT + up * t + 0.5 * GRAVITY * t * t,
                           vz * t)
            self.vel[i] = (vx, up + GRAVITY * t, vz)
            self.life[i] = PARTICLE_LIFETIME - t
            self.col[i] = random.choice(DROP_COLORS)   # losowy kolor z palety
            self.alive[i] = True

    # ---- emisja z uwzglednieniem pulsowania ------------------------------
    def emit(self, dt):
        """Decyduje, czy w tej klatce rodzic krople (pulsowanie lub ciagle)."""
        if not PULSE:
            self.spawn(SPAWN_PER_FRAME)
            return
        self.pulse_timer += dt
        cycle = PULSE_ON + PULSE_OFF
        phase = self.pulse_timer % cycle
        if phase < PULSE_ON:
            self.spawn(SPAWN_PER_FRAME)

    # ---- aktualizacja fizyki ---------------------------------------------
    def update(self, dt):
        a = self.alive
        self.vel[a, 1] += GRAVITY * dt
        self.pos[a] += self.vel[a] * dt
        self.life[a] -= dt
        died = a & ((self.life <= 0) | (self.pos[:, 1] < 0.0))
        self.alive[died] = False

        self.gpu_pos[:] = self.pos
        self.gpu_life[:] = np.where(self.alive,
                                    self.life / PARTICLE_LIFETIME, 0.0)
        self.gpu_col[:] = self.col
        self.pos_data.update(self.gpu_pos)
        self.life_data.update(self.gpu_life)
        self.col_data.update(self.gpu_col)

    # ---- rysowanie point-sprite'ow ---------------------------------------
    def draw(self, projection, view):
        self.material.use()

        proj_u = Uniform("mat4", projection)
        proj_u.find_variable(self.material.program_id, "projection_matrix")
        proj_u.load()
        view_u = Uniform("mat4", view)
        view_u.find_variable(self.material.program_id, "view_matrix")
        view_u.load()
        scale_u = Uniform("float", 140.0)   # bazowy rozmiar punktu (mniej = mniejsze krople)
        scale_u.find_variable(self.material.program_id, "point_scale")
        scale_u.load()
        tex_u = Uniform("sampler2D", (self.sprite_texture, 0))
        tex_u.find_variable(self.material.program_id, "sprite")
        tex_u.load()

        glDepthMask(GL_FALSE)   # czastki nie zapisuja glebi
        glBindVertexArray(self.vao_ref)
        glDrawArrays(GL_POINTS, 0, MAX_PARTICLES)
        glDepthMask(GL_TRUE)