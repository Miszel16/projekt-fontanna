# Fontanna

Animowana, piętrowa fontanna renderowana techniką **point-sprite** w Pythonie
i OpenGL. Scena zawiera teksturowaną podłogę, kamienną fontannę z basenem,
dwoma talerzami, taflę wody oraz animowany strumień kropel.
Kamerą można obracać dookoła fontanny.

## Wymagania

- Python 3.12 lub nowszy (testowane na 3.12 i 3.13)
- Biblioteki: `pygame`, `PyOpenGL`, `numpy`
- Karta graficzna obsługująca OpenGL 3.3


## Sterowanie

| Klawisz            | Działanie                          |
|--------------------|------------------------------------|
| Strzałki ← / →     | obrót kamery dookoła fontanny      |
| Strzałki ↑ / ↓     | podnoszenie / opuszczanie kamery   |
| `+` / `-`          | przybliżanie / oddalanie (zoom)    |
| `Esc`              | wyjście                            |

## Działanie

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


## Dokumentacja

Dokumentacja techniczna znajduje się bezpośrednio w kodzie źródłowym.

Każdy moduł i klasa posiada opis swojego przeznaczenia, a funkcje i metody zostały udokumentowane za pomocą docstringów zawierających:

opis działania,
argumenty wejściowe,
zwracane wartości.

Główna funkcja programu zawiera również opis pełnego przebiegu inicjalizacji, aktualizacji oraz renderowania sceny.


## Release
v1.0.0

Pierwsze kompletne wydanie projektu.

Wersja obejmuje:

kompletną scenę 3D,
proceduralny model piętrowej fontanny,
teksturowane elementy sceny,
powierzchnie wody,
system cząstek renderowany techniką point-sprite,
fizykę ruchu kropli,
kamerę orbitalną,
własne macierze transformacji,
obsługę shaderów, tekstur oraz buforów OpenGL,
dokumentację techniczną kodu,
konfigurację zależności przez requirements.txt.



## Autorzy

- Alicja Plachimowicz
- Mikołaj Rozynek
