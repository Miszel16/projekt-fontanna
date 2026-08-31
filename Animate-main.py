import pygame
from pygame.locals import *
from OpenGL.GL import *

from Material import Material
from Camera import Camera
from Texture import make_sprite_texture
from TextureLoader import load_texture
from SceneMesh import SceneMesh
from FloorMesh import FloorMesh
from FountainMesh import FountainMesh
from WaterMesh import WaterMesh
from Fountain import Fountain
from Transformations import perspective_matrix

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700


def main():
    pygame.init()
    # konfiguracja kontekstu OpenGL pod shadery (jak w lab 17)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Fontanna - point sprites")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)   # shader steruje gl_PointSize

    # --- materialy (programy shaderowe) ---
    scene_material = Material("shaders/scene.vs", "shaders/scene.fs")
    particle_material = Material("shaders/particle.vs", "shaders/particle.fs")
    floor_material = Material("shaders/floor.vs", "shaders/floor.fs")

    # --- obiekty sceny ---
    scene = SceneMesh(scene_material)
    floor_tex = load_texture("textures/KostkaBrukowa.jpg")
    floor = FloorMesh(floor_material, floor_tex)
    fountain_tex = load_texture("textures/fontanna.jpg")
    fountain_mesh = FountainMesh(floor_material, fountain_tex)
    water_tex = load_texture("textures/woda.jpg")
    water = WaterMesh(floor_material, water_tex)
    sprite_tex = make_sprite_texture()
    fountain = Fountain(particle_material, sprite_tex)
    camera = Camera()

    projection = perspective_matrix(
        60.0, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 200.0)

    clock = pygame.time.Clock()
    done = False
    while not done:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                done = True

        # --- logika ---
        camera.update(dt)
        fountain.emit(dt)          # emisja z pulsowaniem (patrz Fountain.py: PULSE)
        fountain.update(dt)
        view = camera.get_VM()

        # --- rysowanie ---
        glClearColor(0.53, 0.81, 0.92, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        scene.draw(projection, view)       # niebo
        floor.draw(projection, view)       # teksturowana podloga (kostka)
        fountain_mesh.draw(projection, view)  # teksturowana fontanna (kamien)
        water.draw(projection, view)       # teksturowane tafle wody
        fountain.draw(projection, view)    # point-sprite (woda tryskajaca)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()