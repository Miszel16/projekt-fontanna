"""
Moduł implementujący system cząsteczek reprezentujących wodę fontanny.

Odpowiada za generowanie nowych kropli, przechowywanie ich parametrów,
aktualizację ruchu pod wpływem grawitacji oraz przesyłanie aktualnych
danych cząsteczek do GPU.

Cząsteczki renderowane są jako punkty OpenGL wykorzystujące teksturę
sprite'a do uzyskania wyglądu pojedynczych kropli wody.
"""

import math
import random
import numpy as np
from OpenGL.GL import *
from GraphicsData import GraphicsData
from Uniform import Uniform
from Settings import EMIT_HEIGHT, LOWER_BOWL_Y, UPPER_BOWL_Y, COLUMN_HEIGHT   # geometria wspolna ze scena

MAX_PARTICLES = 2000        # maksymalna liczba kropli (z zapasem na rozbryzgi)
SPAWN_PER_FRAME = 1        # ile nowych kropli rodzi sie na klatke
GRAVITY = -9.8             # przyspieszenie grawitacyjne
PARTICLE_LIFETIME = 2.4     # czas zycia kropli (s)
POINT_SCALE = 140.0          # bazowy rozmiar kropli (mniej = mniejsze krople)

# --- ROZBRYZG NA TAFLI WODY ------------------------------------------------
# Kropla, ktora dotknie tafli basenu, znika i tworzy kilka mniejszych kropli
# "plusku" lecacych w gore i na boki. Krople rozbryzgu NIE tworza kolejnego
# rozbryzgu (zabezpieczenie przed lawina czastek).
WATER_LEVEL = 0.2          # wysokosc tafli basenu (h*0.4 z WaterMesh, h=0.5)
SPLASH_COUNT = 4           # ile malych kropli powstaje z jednego plusku
SPLASH_UP = 2.6            # predkosc pionowa kropli rozbryzgu (nizej niz glowny strumien)
SPLASH_SIDE = 1.8          # predkosc pozioma rozbryzgu (rozrzut na boki)
SPLASH_LIFETIME = 0.9      # krotkie zycie kropli rozbryzgu (s)
SPLASH_SIZE = 0.6          # mnoznik rozmiaru kropli rozbryzgu (mniejsze od glownych)

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

# --- KOLIZJA Z GEOMETRIA MURKOW --------------------------------------------
# Kazda scianka (murek) opisana jest jako pierscien: promien wewnetrzny,
# promien zewnetrzny oraz zakres wysokosci [y_dol, y_gora]. Kropla, ktora
# znajdzie sie WEWNATRZ takiej bryly, uderzyla w murek i znika. Wartosci
# odpowiadaja geometrii z FountainMesh (basen: r_in=2.6, r_out=3.2, h=0.5;
# talerze: grubosc scianki tw=0.25, wysokosc th=0.28).
# --- SLUP-STOZEK (do kolizji) ----------------------------------------------
# Slup jest stozkiem: promien maleje liniowo z wysokoscia od COLUMN_BOTTOM_R
# (u podstawy) do COLUMN_TOP_R (u szczytu). Wartosci zgodne z FountainMesh.
COLUMN_BOTTOM_R = 0.55
COLUMN_TOP_R = 0.15


WALLS = [
    # (r_wewn, r_zewn, y_dol, y_gora)
    (2.6, 3.2, 0.0, 0.5),                                   # murek basenu
    (1.25, 1.5, LOWER_BOWL_Y, LOWER_BOWL_Y + 0.28),         # murek dolnego talerza
    (0.75, 1.0, UPPER_BOWL_Y, UPPER_BOWL_Y + 0.28),         # murek gornego talerza
]

# --- TAFLE WODY (do rozbryzgu) ---------------------------------------------
# Kazda tafla: (poziom_y, promien). Kropla spadajaca na dana tafle w obrebie
# jej promienia robi plusk i znika. Poziomy zgodne z WaterMesh (tafle talerzy
# na base_y + th*0.5, th=0.28; promienie wewnetrzne mis).
WATER_SURFACES = [
    (WATER_LEVEL, 2.6),                                     # tafla basenu
    (LOWER_BOWL_Y + 0.28 * 0.5, 1.25),                     # tafla dolnego talerza
    (UPPER_BOWL_Y + 0.28 * 0.5, 0.75),                     # tafla gornego talerza
]


class Fountain:
    """
    Reprezentuje system cząsteczek tworzących strumień wody fontanny.

    Klasa zarządza pozycją, prędkością, czasem życia i kolorem
    wszystkich cząsteczek oraz odpowiada za ich emisję,
    aktualizację fizyki i renderowanie.
    """

    def __init__(self, material, sprite_texture):
        """
        Inicjalizuje system cząsteczek fontanny.

        Tworzy tablice przechowujące pozycje, prędkości, czas życia,
        kolory, rozmiar, kąt obrotu oraz oznaczenie kropli rozbryzgu
        i stan cząsteczek. Przygotowuje również VAO oraz dynamiczne
        bufory danych przekazywane do vertex shadera.

        Args:
            material (Material): Materiał zawierający program shaderowy
                używany do renderowania cząsteczek.
            sprite_texture: Tekstura używana do renderowania pojedynczej kropli.

        Returns:
            None
        """
        self.material = material
        self.sprite_texture = sprite_texture

        self.pos = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.vel = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.life = np.zeros(MAX_PARTICLES, np.float32)
        self.max_life = np.full(MAX_PARTICLES, PARTICLE_LIFETIME, np.float32)  # czas zycia danej kropli
        self.col = np.zeros((MAX_PARTICLES, 3), np.float32)   # kolor kropli
        self.size = np.ones(MAX_PARTICLES, np.float32)        # mnoznik rozmiaru kropli
        self.angle = np.zeros(MAX_PARTICLES, np.float32)      # kat obrotu lezki (kierunek lotu)
        self.is_splash = np.zeros(MAX_PARTICLES, bool)        # czy kropla powstala z rozbryzgu
        self.alive = np.zeros(MAX_PARTICLES, bool)
        self.next_idx = 0
        self.pulse_timer = 0.0     # zegar do sterowania pulsowaniem

        self.gpu_pos = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.gpu_life = np.zeros(MAX_PARTICLES, np.float32)
        self.gpu_col = np.zeros((MAX_PARTICLES, 3), np.float32)
        self.gpu_angle = np.zeros(MAX_PARTICLES, np.float32)
        self.gpu_size = np.zeros(MAX_PARTICLES, np.float32)

        self.vao_ref = glGenVertexArrays(1)
        glBindVertexArray(self.vao_ref)
        self.pos_data = GraphicsData("vec3", self.gpu_pos, GL_DYNAMIC_DRAW)
        self.pos_data.create_variable(material.program_id, "position")
        self.life_data = GraphicsData("float", self.gpu_life, GL_DYNAMIC_DRAW)
        self.life_data.create_variable(material.program_id, "life")
        self.col_data = GraphicsData("vec3", self.gpu_col, GL_DYNAMIC_DRAW)
        self.col_data.create_variable(material.program_id, "color")
        self.angle_data = GraphicsData("float", self.gpu_angle, GL_DYNAMIC_DRAW)
        self.angle_data.create_variable(material.program_id, "angle")
        self.size_data = GraphicsData("float", self.gpu_size, GL_DYNAMIC_DRAW)
        self.size_data.create_variable(material.program_id, "psize")

    # ---- Nowe krople -----------------------------------------
    def spawn(self, n):
        """
        Generuje określoną liczbę nowych cząsteczek fontanny.

        Dla każdej cząsteczki losuje kierunek ruchu poziomego,
        prędkość pionową oraz początkowy moment jej trajektorii.
        Na tej podstawie wyznacza początkową pozycję, prędkość,
        pozostały czas życia, kolor, rozmiar oraz kąt obrotu kropli.
        Cząsteczki tworzone tą metodą są kroplami głównego strumienia
        (nie są rozbryzgiem).

        Args:
            n (int): Liczba nowych cząsteczek do wygenerowania.

        Returns:
            None
        """
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
            self.max_life[i] = PARTICLE_LIFETIME
            self.col[i] = random.choice(DROP_COLORS)   # losowy kolor z palety
            self.size[i] = 1.0                         # glowna kropla: pelny rozmiar
            self.is_splash[i] = False                  # to nie rozbryzg
            self.alive[i] = True

    # ---- emisja z uwzglednieniem pulsowania ------------------------------
    def emit(self, dt):
        """
        Steruje emisją nowych cząsteczek fontanny.

        Przy wyłączonym trybie pulsacyjnym generuje nowe cząsteczki
        w każdej klatce. Przy włączonym pulsowaniu wykorzystuje licznik
        czasu do naprzemiennego włączania i zatrzymywania emisji.

        Args:
            dt (float): Czas od poprzedniej klatki wyrażony w sekundach.

        Returns:
            None
        """
        # Decyduje, czy w tej klatce rodzic krople (pulsowanie lub ciagle).
        if not PULSE:
            self.spawn(SPAWN_PER_FRAME)
            return
        self.pulse_timer += dt
        cycle = PULSE_ON + PULSE_OFF
        phase = self.pulse_timer % cycle
        if phase < PULSE_ON:
            self.spawn(SPAWN_PER_FRAME)

    # ---- rozbryzg na tafli wody ------------------------------------------
    def _emit_splash(self, x, y, z, color):
        """
        Tworzy krople rozbryzgu w miejscu uderzenia kropli o taflę.

        W zadanym punkcie generuje SPLASH_COUNT małych kropli lecących
        w górę i na boki (efekt plusku). Krople rozbryzgu mają krótki
        czas życia, mniejszy rozmiar oraz oznaczenie is_splash, dzięki
        czemu same nie wywołują kolejnego rozbryzgu.

        Args:
            x (float): Współrzędna X miejsca uderzenia.
            y (float): Współrzędna Y miejsca uderzenia (poziom tafli).
            z (float): Współrzędna Z miejsca uderzenia.
            color: Kolor RGB dziedziczony po kropli, która uderzyła.

        Returns:
            None
        """
        for _ in range(SPLASH_COUNT):
            i = self.next_idx
            self.next_idx = (self.next_idx + 1) % MAX_PARTICLES
            ang = random.uniform(0, 2 * math.pi)
            side = random.uniform(0.3, 1.0) * SPLASH_SIDE
            self.pos[i] = (x, y, z)
            self.vel[i] = (math.cos(ang) * side,
                           random.uniform(0.6, 1.0) * SPLASH_UP,   # gora
                           math.sin(ang) * side)
            self.life[i] = SPLASH_LIFETIME
            self.max_life[i] = SPLASH_LIFETIME
            self.col[i] = color
            self.size[i] = SPLASH_SIZE                 # mniejsze od glownych
            self.is_splash[i] = True                   # rozbryzg nie rozbryzguje sie ponownie
            self.alive[i] = True

    def _splash(self):
        """
        Obsługuje rozbryzg cząsteczek uderzających w tafle wody.

        Sprawdza wszystkie tafle wody fontanny (basen oraz oba talerze,
        zdefiniowane w WATER_SURFACES). Dla każdej tafli wyszukuje aktywne,
        opadające krople, które osiągnęły jej poziom, znajdując się w obrębie
        promienia danej tafli. Krople głównego strumienia tworzą w miejscu
        uderzenia mniejsze krople rozbryzgu (metoda _emit_splash) i znikają,
        natomiast krople będące już rozbryzgiem po prostu znikają, nie
        wywołując kolejnych rozbryzgów.

        Args:
            Brak.

        Returns:
            None
        """
        radial = np.hypot(self.pos[:, 0], self.pos[:, 2])
        for level, radius in WATER_SURFACES:
            # krople opadajace, ktore osiagnely dana tafle w obrebie jej promienia
            hit = (self.alive
                   & (self.vel[:, 1] < 0.0)
                   & (self.pos[:, 1] <= level)
                   & (self.pos[:, 1] > level - 0.25)   # tylko tuz przy tej tafli
                   & (radial <= radius))
            # glowne krople -> rozbryzg; krople rozbryzgu -> tylko znikaja
            main_hit = np.nonzero(hit & (~self.is_splash))[0]
            for i in main_hit:
                self._emit_splash(self.pos[i, 0], level, self.pos[i, 2],
                                  tuple(self.col[i]))
            self.alive[hit] = False

    # ---- kolizja z geometria murkow --------------------------------------
    def _collide_walls(self):
        """
        Usuwa cząsteczki, które zderzyły się z geometrią murków fontanny.

        Dla każdego murku (basenu oraz obu talerzy) sprawdza, czy aktywna
        kropla znajduje się wewnątrz jego bryły — to znaczy jej odległość
        od osi mieści się między wewnętrznym a zewnętrznym promieniem murku,
        a jej wysokość mieści się w zakresie wysokości ścianki. Krople
        spełniające ten warunek uderzyły w murek i zostają dezaktywowane,
        dzięki czemu nie przenikają przez ceglane ścianki.

        Args:
            Brak.

        Returns:
            None
        """
        # odleglosc kazdej kropli od pionowej osi fontanny (promien walcowy)
        radial = np.hypot(self.pos[:, 0], self.pos[:, 2])
        y = self.pos[:, 1]
        for r_in, r_out, y_lo, y_hi in WALLS:
            inside = (self.alive
                      & (radial >= r_in) & (radial <= r_out)
                      & (y >= y_lo) & (y <= y_hi))
            self.alive[inside] = False

    # ---- kolizja ze slupem-stozkiem --------------------------------------
    def _collide_column(self):
        """
        Usuwa cząsteczki, które zderzyły się z centralnym słupem fontanny.

        Słup ma kształt stożka, więc jego promień maleje liniowo wraz
        z wysokością — od COLUMN_BOTTOM_R u podstawy do COLUMN_TOP_R
        u szczytu (na wysokości COLUMN_HEIGHT). Dla każdej aktywnej kropli
        w zakresie wysokości słupa wyznaczany jest promień stożka na jej
        wysokości; jeśli kropla znajduje się bliżej osi niż ten promień,
        oznacza to kontakt ze słupem i kropla zostaje dezaktywowana.

        Args:
            Brak.

        Returns:
            None
        """
        y = self.pos[:, 1]
        radial = np.hypot(self.pos[:, 0], self.pos[:, 2])
        # w zakresie wysokosci slupa
        in_height = self.alive & (y >= 0.0) & (y <= COLUMN_HEIGHT)
        # promien stozka na wysokosci y (liniowa interpolacja dol->gora)
        frac = np.clip(y / COLUMN_HEIGHT, 0.0, 1.0)
        cone_r = COLUMN_BOTTOM_R + (COLUMN_TOP_R - COLUMN_BOTTOM_R) * frac
        inside = in_height & (radial <= cone_r)
        self.alive[inside] = False

    # ---- aktualizacja fizyki ---------------------------------------------
    def update(self, dt):
        """
        Aktualizuje fizykę i stan wszystkich aktywnych cząsteczek.

        Uwzględnia działanie grawitacji, aktualizuje pozycję oraz
        pozostały czas życia kropli. Wyznacza kąt obrotu łezki na
        podstawie kierunku lotu, obsługuje rozbryzg kropli uderzających
        w taflę wody (metoda _splash), kolizję z geometrią murków
        (metoda _collide_walls) oraz kolizję z centralnym słupem
        (metoda _collide_column). Dezaktywuje cząsteczki, które zakończyły
        czas życia lub spadły poniżej poziomu sceny.

        Po zakończeniu obliczeń aktualne dane cząsteczek (pozycja, czas
        życia, kolor, kąt) są przesyłane do dynamicznych buforów GPU.

        Args:
            dt (float): Czas od poprzedniej klatki wyrażony w sekundach.

        Returns:
            None
        """
        a = self.alive
        self.vel[a, 1] += GRAVITY * dt
        self.pos[a] += self.vel[a] * dt
        self.life[a] -= dt

        # rozbryzg na tafli wody (tworzy male krople, glowne znikaja)
        self._splash()

        # kolizja z geometria murkow - krople uderzajace w scianki znikaja
        self._collide_walls()

        # kolizja z centralnym slupem-stozkiem
        self._collide_column()

        # kat obrotu lezki: czubek przeciwnie do kierunku lotu.
        # znak "-" przy skladowej poziomej koryguje obrot w bok (lustrzane
        # odbicie), zachowujac poprawny kierunek przy locie w gore i w dol.
        self.angle[a] = np.arctan2(-self.vel[a, 0], self.vel[a, 1])

        died = a & ((self.life <= 0) | (self.pos[:, 1] < 0.0))
        self.alive[died] = False

        self.gpu_pos[:] = self.pos
        self.gpu_life[:] = np.where(self.alive,
                                    self.life / self.max_life, 0.0)
        self.gpu_col[:] = self.col
        self.gpu_angle[:] = self.angle
        self.gpu_size[:] = np.where(self.alive, self.size, 0.0)
        self.pos_data.update(self.gpu_pos)
        self.life_data.update(self.gpu_life)
        self.col_data.update(self.gpu_col)
        self.angle_data.update(self.gpu_angle)
        self.size_data.update(self.gpu_size)

    # ---- rysowanie point-sprite'ow ---------------------------------------
    def draw(self, projection, view):
        """
        Renderuje wszystkie cząsteczki fontanny.

        Aktywuje materiał cząsteczek, przekazuje do shaderów macierz
        projekcji, macierz widoku, skalę punktów oraz teksturę sprite'a.
        Następnie renderuje cząsteczki jako punkty OpenGL.

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
        scale_u = Uniform("float", POINT_SCALE)   # bazowy rozmiar punktu (stala u gory pliku)
        scale_u.find_variable(self.material.program_id, "point_scale")
        scale_u.load()
        tex_u = Uniform("sampler2D", (self.sprite_texture, 0))
        tex_u.find_variable(self.material.program_id, "sprite")
        tex_u.load()

        glDepthMask(GL_FALSE)   # czastki nie zapisuja glebi
        glBindVertexArray(self.vao_ref)
        glDrawArrays(GL_POINTS, 0, MAX_PARTICLES)
        glDepthMask(GL_TRUE)