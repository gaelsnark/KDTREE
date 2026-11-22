"""
BFS (Breadth-First Search) para MiniMouse

El ratón busca la salida del laberinto con una búsqueda en anchura (BFS).
Como BFS expande las celdas por "capas" de distancia, el primer camino que
llega a la meta es siempre el MÁS CORTO (en número de pasos).

Diseño:
    El BFS NO sabe cómo está guardado el laberinto. Solo necesita una función
    `obtener_vecinos(celda)` que le diga a qué celdas puede moverse. Esa función
    se construye a partir de un "sensor" de búsqueda por rango ortogonal:

        - KD-Tree      -> Build&Search.py   (celdas libres)
        - Fuerza bruta -> fuerzabruta.py    (paredes o celdas libres)

    Así podemos comparar ambos métodos con el MISMO BFS.

Convención de coordenadas (igual que KD-Tree y fuerzabruta.py):
    (x, y) = (columna, fila)
    Rango de búsqueda R = ((xmin, xmax), (ymin, ymax))

Ejecutar demo:
    python Minimouse/bfs.py
"""

import contextlib
import importlib.util
import io
from collections import deque
from dataclasses import dataclass
from pathlib import Path

# Movimientos ortogonales (dx, dy): arriba, derecha, abajo, izquierda.
# El orden fija un resultado determinista cuando hay varios caminos igual de cortos.
DIRECCIONES = ((0, -1), (1, 0), (0, 1), (-1, 0))


# ---------------------------------------------------------------------------
# 1. Algoritmo BFS
# ---------------------------------------------------------------------------

@dataclass
class ResultadoBFS:
    encontrado: bool     # True si existe camino hasta la meta
    camino: list         # [inicio, ..., meta]  (vacío si no hay camino)
    explorados: list     # celdas en el orden en que BFS las descubrió
    padres: dict         # celda -> celda desde la que se descubrió

    @property
    def pasos(self):
        """Número de movimientos del camino (None si no hay camino)."""
        return len(self.camino) - 1 if self.encontrado else None


def reconstruir_camino(padres, meta):
    """Sigue los padres desde la meta hasta el inicio y devuelve el camino."""
    camino = []
    celda = meta
    while celda is not None:
        camino.append(celda)
        celda = padres[celda]
    camino.reverse()
    return camino


def bfs(inicio, meta, obtener_vecinos):
    """
    Búsqueda en anchura desde `inicio` hasta `meta`.

    :param inicio: celda inicial (x, y)
    :param meta: celda de salida (x, y)
    :param obtener_vecinos: función celda -> lista de celdas alcanzables
    :return: ResultadoBFS

    Complejidad: se expande cada celda a lo sumo una vez, O(V) consultas
    al sensor (V = celdas libres) y O(V + E) de trabajo propio del BFS.
    """
    padres = {inicio: None}          # también funciona como conjunto de visitados
    explorados = [inicio]

    if inicio == meta:
        return ResultadoBFS(True, [inicio], explorados, padres)

    cola = deque([inicio])
    while cola:
        actual = cola.popleft()

        for vecino in obtener_vecinos(actual):
            if vecino in padres:     # ya descubierto
                continue

            padres[vecino] = actual
            explorados.append(vecino)

            # Con BFS, la primera vez que descubrimos la meta ya es el camino más corto
            if vecino == meta:
                return ResultadoBFS(
                    True, reconstruir_camino(padres, meta), explorados, padres
                )

            cola.append(vecino)

    return ResultadoBFS(False, [], explorados, padres)


# ---------------------------------------------------------------------------
# 2. Sensores: de "búsqueda por rango" a "vecinos de una celda"
# ---------------------------------------------------------------------------

def vecinos_desde_libres(buscar_rango):
    """
    Para sensores cuyos puntos son CELDAS LIBRES (como el KD-Tree de la clase Mouse).

    Consulta la caja 3x3 alrededor de la celda y se queda con los 4 vecinos
    ortogonales (distancia de Manhattan = 1) que aparezcan como libres.
    """
    def obtener_vecinos(celda):
        x, y = celda
        libres = set(buscar_rango(((x - 1, x + 1), (y - 1, y + 1))))
        return [
            (x + dx, y + dy)
            for dx, dy in DIRECCIONES
            if (x + dx, y + dy) in libres
        ]
    return obtener_vecinos


def vecinos_desde_paredes(buscar_rango, ancho, alto):
    """
    Para sensores cuyos puntos son PAREDES (como fuerzabruta.py).

    Un vecino es válido si está dentro del laberinto y NO aparece
    entre las paredes detectadas en la caja 3x3.
    """
    def obtener_vecinos(celda):
        x, y = celda
        paredes = set(buscar_rango(((x - 1, x + 1), (y - 1, y + 1))))
        vecinos = []
        for dx, dy in DIRECCIONES:
            nx, ny = x + dx, y + dy
            if 0 <= nx < ancho and 0 <= ny < alto and (nx, ny) not in paredes:
                vecinos.append((nx, ny))
        return vecinos
    return obtener_vecinos


class SensorConContador:
    """Envuelve un sensor y cuenta cuántas consultas recibe (útil para comparar)."""

    def __init__(self, buscar_rango):
        self.buscar_rango = buscar_rango
        self.consultas = 0

    def __call__(self, rango):
        self.consultas += 1
        return self.buscar_rango(rango)


def crear_sensor_fuerza_bruta(puntos):
    """Sensor de fuerza bruta O(n): misma lógica que fuerzaBruta() de fuerzabruta.py."""
    def buscar_rango(rango):
        (xmin, xmax), (ymin, ymax) = rango
        return [(x, y) for x, y in puntos if xmin <= x <= xmax and ymin <= y <= ymax]
    return buscar_rango


def cargar_modulo_kdtree():
    """
    Carga KD-Tree/Build&Search.py. No se puede usar `import` normal porque el
    nombre tiene '&' y la carpeta tiene '-'. Se silencia su demo de arranque.
    Devuelve el módulo, o None si el archivo no existe.
    """
    ruta = Path(__file__).resolve().parent.parent / "KD-Tree" / "Build&Search.py"
    if not ruta.exists():
        return None

    spec = importlib.util.spec_from_file_location("kd_build_search", ruta)
    modulo = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(modulo)
    return modulo


def crear_sensor_kdtree(puntos):
    """Construye el KD-Tree con `puntos` y devuelve su función de búsqueda por rango."""
    modulo = cargar_modulo_kdtree()
    if modulo is None:
        raise FileNotFoundError("No se encontró KD-Tree/Build&Search.py")

    raiz = modulo.build_kd_tree(list(puntos))
    return lambda rango: modulo.search_kd_tree(raiz, rango)


# ---------------------------------------------------------------------------
# 3. Laberintos en texto (mismo formato que fuerzabruta.py)
# ---------------------------------------------------------------------------
#   #  pared      .  camino libre      M  inicio del ratón      E  salida

@dataclass
class Laberinto:
    paredes: set
    libres: set
    inicio: tuple
    meta: tuple
    ancho: int
    alto: int


def leer_laberinto(lineas):
    """
    Convierte una lista de strings en un Laberinto.
    Las filas más cortas se completan con pared (el laberinto de ejemplo de
    fuerzabruta.py tiene filas de distinto largo).
    """
    alto = len(lineas)
    ancho = max(len(linea) for linea in lineas)
    paredes, libres = set(), set()
    inicio = meta = None

    for y in range(alto):
        for x in range(ancho):
            c = lineas[y][x] if x < len(lineas[y]) else "#"
            if c in ".ME":
                libres.add((x, y))
                if c == "M":
                    inicio = (x, y)
                elif c == "E":
                    meta = (x, y)
            else:
                paredes.add((x, y))

    return Laberinto(paredes, libres, inicio, meta, ancho, alto)


def dibujar_camino(lineas, camino):
    """Devuelve el laberinto en texto marcando el camino con '*'."""
    ancho = max(len(linea) for linea in lineas)
    filas = [list(linea.ljust(ancho, "#")) for linea in lineas]
    for x, y in camino:
        if filas[y][x] == ".":
            filas[y][x] = "*"
    return ["".join(f) for f in filas]


# ---------------------------------------------------------------------------
# 4. Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    laberinto_texto = [
        "#####",
        "#M..#",
        "#.#.###",
        "#.#..E#",
        "#######",
    ]

    lab = leer_laberinto(laberinto_texto)
    print("Laberinto:")
    print("\n".join(laberinto_texto))

    # Mismo BFS, tres formas distintas de "sentir" el laberinto
    sensores = {
        "Fuerza bruta (celdas libres)": vecinos_desde_libres(
            crear_sensor_fuerza_bruta(lab.libres)
        ),
        "Fuerza bruta (paredes)": vecinos_desde_paredes(
            crear_sensor_fuerza_bruta(lab.paredes), lab.ancho, lab.alto
        ),
    }
    try:
        sensores["KD-Tree (celdas libres)"] = vecinos_desde_libres(
            crear_sensor_kdtree(lab.libres)
        )
    except FileNotFoundError:
        pass

    for nombre, vecinos in sensores.items():
        r = bfs(lab.inicio, lab.meta, vecinos)
        print(f"\n[{nombre}]")
        print("Encontrado:", r.encontrado, "| Pasos:", r.pasos,
              "| Explorados:", len(r.explorados))
        print("Camino:", r.camino)

    print("\nCamino marcado con '*':")
    resultado = bfs(lab.inicio, lab.meta, list(sensores.values())[0])
    print("\n".join(dibujar_camino(laberinto_texto, resultado.camino)))
