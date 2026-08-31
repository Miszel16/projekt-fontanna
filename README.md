# Fontanna

Animowana, piętrowa fontanna renderowana techniką **point-sprite** w Pythonie
i OpenGL. Scena zawiera teksturowaną podłogę, kamienną fontannę z basenem,
dwoma talerzami, taflę wody oraz animowany strumień kropel.
Kamerą można obracać dookoła fontanny.

## Wymagania

- Python 3.12 lub nowszy (testowane na 3.12 i 3.13)
- Biblioteki: `pygame`, `PyOpenGL`, `numpy`
- Karta graficzna obsługująca OpenGL 3.3

## Instalacja i uruchomienie

W folderze projektu:

```bash
# 1. Utwórz środowisko wirtualne
py -3.12 -m venv venv           # lub: py -3.13 -m venv venv

# 2. Aktywuj je
venv\Scripts\Activate.ps1       # Windows PowerShell
# venv\Scripts\activate.bat     # Windows cmd
# source venv/bin/activate      # Linux / macOS

# 3. Zainstaluj biblioteki
python -m pip install -r requirements.txt

# 4. Uruchom
python Animate-main.py
```

## Sterowanie

| Klawisz            | Działanie                          |
|--------------------|------------------------------------|
| Strzałki ← / →     | obrót kamery dookoła fontanny      |
| Strzałki ↑ / ↓     | podnoszenie / opuszczanie kamery   |
| `+` / `-`          | przybliżanie / oddalanie (zoom)    |
| `Esc`              | wyjście                            |

## Jak to działa (użyte techniki)

- **Point-sprite** - strumień wody to teksturowane punkty `GL_POINTS`.
  Shader wierzchołków ustawia `gl_PointSize` (rozmiar maleje z odległością od
  kamery), a shader fragmentów używa `gl_PointCoord` do nałożenia tekstury
  kropli na każdy punkt.
- **System cząstek** - własna implementacja: każda kropla rodzi się na szczycie
  słupa z prędkością w górę i losowym rozrzutem, działa na nią grawitacja, a po
  upływie czasu życia odradza się jako nowa. Obliczenia wektorowe w NumPy.
- **Teksturowanie z kafelkowaniem** - podłoga, fontanna i tafla wody mają
  współrzędne UV i teksturę z `GL_REPEAT`, dzięki czemu tekstura powtarza się
  po powierzchni. Filtrowanie z mipmapami ogranicza migotanie w oddali.
- **Własne macierze** - perspektywa i macierz widoku (look_at) liczone ręcznie,
  bez gotowych silników 3D. Rendering oparty jest bezpośrednio na OpenGL
  (PyOpenGL), pygame dostarcza okno i obsługę klawiatury.

## Struktura projektu

```
Animate-main.py     - główny plik, pętla renderowania i złożenie sceny
Settings.py         - wspólne parametry (m.in. wysokość słupa)

Material.py         - program shaderowy (kompilacja + użycie)
Utils.py            - kompilacja i linkowanie shaderów
GraphicsData.py     - bufory VBO atrybutów wierzchołków
Uniform.py          - przekazywanie macierzy/wektorów/tekstur do shaderów
Transformations.py  - macierze perspektywy i widoku
Camera.py           - kamera orbitująca dookoła fontanny

SceneMesh.py        - niebo
FloorMesh.py        - teksturowana podłoga
FountainMesh.py     - kamienne bryły fontanny (basen, talerze, słup)
WaterMesh.py        - tafle wody
Fountain.py         - system cząstek (point-sprite)
Texture.py          - proceduralna tekstura kropli
TextureLoader.py    - wczytywanie tekstur z plików

shaders/            - kod shaderów GLSL (scene, floor, particle)
textures/           - obrazy tekstur (podłoga, fontanna, woda)
```

## Autorzy

- Alicja Plachimowicz
- Mikołaj Rozynek
