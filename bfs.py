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

import contextlib                      # para silenciar la salida de otro módulo
import importlib.util                  # para cargar un archivo .py por su ruta
import io                              # StringIO sirve como "papelera" de texto
from collections import deque          # cola eficiente (sacar por la izquierda en O(1))
from dataclasses import dataclass      # crea clases de datos sin escribir __init__
from pathlib import Path               # manejo de rutas de archivos

# Movimientos ortogonales (dx, dy): arriba, derecha, abajo, izquierda.
# El orden fija un resultado determinista cuando hay varios caminos igual de cortos.
DIRECCIONES = ((0, -1), (1, 0), (0, 1), (-1, 0))  # tupla con los 4 movimientos posibles


# ---------------------------------------------------------------------------
# 1. Algoritmo BFS
# ---------------------------------------------------------------------------

@dataclass                             # genera __init__ y __repr__ automáticamente
class ResultadoBFS:
    encontrado: bool     # True si existe camino hasta la meta
    camino: list         # [inicio, ..., meta]  (vacío si no hay camino)
    explorados: list     # celdas en el orden en que BFS las descubrió
    padres: dict         # celda -> celda desde la que se descubrió

    @property                          # permite usar r.pasos sin paréntesis
    def pasos(self):
        """Número de movimientos del camino (None si no hay camino)."""
        return len(self.camino) - 1 if self.encontrado else None  # pasos = celdas - 1


def reconstruir_camino(padres, meta):
    """Sigue los padres desde la meta hasta el inicio y devuelve el camino."""
    camino = []                        # lista donde se guardará el camino (al revés)
    celda = meta                       # empezamos en la meta
    while celda is not None:           # el inicio tiene padre None, ahí se detiene
        camino.append(celda)           # guardamos la celda actual
        celda = padres[celda]          # retrocedemos a la celda que la descubrió
    camino.reverse()                   # invertimos para que quede inicio -> meta
    return camino                      # devolvemos el camino ordenado


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
    padres = {inicio: None}            # también funciona como conjunto de visitados
    explorados = [inicio]              # orden de descubrimiento (para animar)

    if inicio == meta:                 # caso especial: ya estamos en la salida
        return ResultadoBFS(True, [inicio], explorados, padres)  # camino de 0 pasos

    cola = deque([inicio])             # cola FIFO con la frontera de exploración
    while cola:                        # mientras queden celdas por expandir
        actual = cola.popleft()        # sacamos la celda más antigua (la más cercana)

        for vecino in obtener_vecinos(actual):  # preguntamos al sensor a dónde podemos ir
            if vecino in padres:       # si ya fue descubierta...
                continue               # ...la ignoramos para no repetir

            padres[vecino] = actual    # anotamos desde dónde llegamos al vecino
            explorados.append(vecino)  # lo registramos en el orden de descubrimiento

            # Con BFS, la primera vez que descubrimos la meta ya es el camino más corto
            if vecino == meta:         # ¿encontramos la salida?
                return ResultadoBFS(   # sí: armamos y devolvemos el resultado
                    True, reconstruir_camino(padres, meta), explorados, padres
                )

            cola.append(vecino)        # si no es la meta, lo expandiremos más adelante

    return ResultadoBFS(False, [], explorados, padres)  # la cola se vació: no hay salida


# ---------------------------------------------------------------------------
# 2. Sensores: de "búsqueda por rango" a "vecinos de una celda"
# ---------------------------------------------------------------------------

def vecinos_desde_libres(buscar_rango):
    """
    Para sensores cuyos puntos son CELDAS LIBRES (como el KD-Tree de la clase Mouse).

    Consulta la caja 3x3 alrededor de la celda y se queda con los 4 vecinos
    ortogonales (distancia de Manhattan = 1) que aparezcan como libres.
    """
    def obtener_vecinos(celda):        # función que BFS usará para pedir vecinos
        x, y = celda                   # separamos las coordenadas de la celda
        libres = set(buscar_rango(((x - 1, x + 1), (y - 1, y + 1))))  # celdas libres en la caja 3x3
        return [                       # devolvemos solo los vecinos ortogonales libres
            (x + dx, y + dy)           # coordenada del vecino en esa dirección
            for dx, dy in DIRECCIONES  # probamos arriba, derecha, abajo, izquierda
            if (x + dx, y + dy) in libres  # solo si el sensor lo reportó como libre
        ]
    return obtener_vecinos             # devolvemos la función ya configurada


def vecinos_desde_paredes(buscar_rango, ancho, alto):
    """
    Para sensores cuyos puntos son PAREDES (como fuerzabruta.py).

    Un vecino es válido si está dentro del laberinto y NO aparece
    entre las paredes detectadas en la caja 3x3.
    """
    def obtener_vecinos(celda):        # función que BFS usará para pedir vecinos
        x, y = celda                   # separamos las coordenadas de la celda
        paredes = set(buscar_rango(((x - 1, x + 1), (y - 1, y + 1))))  # paredes en la caja 3x3
        vecinos = []                   # aquí se guardan los vecinos válidos
        for dx, dy in DIRECCIONES:     # probamos las 4 direcciones
            nx, ny = x + dx, y + dy    # coordenada del vecino candidato
            if 0 <= nx < ancho and 0 <= ny < alto and (nx, ny) not in paredes:  # dentro y sin pared
                vecinos.append((nx, ny))  # es transitable: lo agregamos
        return vecinos                 # lista de vecinos transitables
    return obtener_vecinos             # devolvemos la función ya configurada


class SensorConContador:
    """Envuelve un sensor y cuenta cuántas consultas recibe (útil para comparar)."""

    def __init__(self, buscar_rango):  # recibe el sensor real a envolver
        self.buscar_rango = buscar_rango  # guardamos el sensor original
        self.consultas = 0             # contador de consultas, empieza en cero

    def __call__(self, rango):         # permite usar el objeto como si fuera una función
        self.consultas += 1            # cada llamada suma una consulta
        return self.buscar_rango(rango)  # delegamos la búsqueda al sensor real


def crear_sensor_fuerza_bruta(puntos):
    """Sensor de fuerza bruta O(n): misma lógica que fuerzaBruta() de fuerzabruta.py."""
    def buscar_rango(rango):           # función de búsqueda que se devolverá
        (xmin, xmax), (ymin, ymax) = rango  # desempaquetamos los límites del rectángulo
        return [(x, y) for x, y in puntos if xmin <= x <= xmax and ymin <= y <= ymax]  # revisa TODOS los puntos
    return buscar_rango                # devolvemos el sensor listo para usar


def cargar_modulo_kdtree():
    """
    Carga KD-Tree/Build&Search.py. No se puede usar `import` normal porque el
    nombre tiene '&' y la carpeta tiene '-'. Se silencia su demo de arranque.
    Devuelve el módulo, o None si el archivo no existe.
    """
    ruta = Path(__file__).resolve().parent.parent / "KD-Tree" / "Build&Search.py"  # ruta relativa a este archivo
    if not ruta.exists():              # si el archivo no está en el repo...
        return None                    # ...avisamos devolviendo None

    spec = importlib.util.spec_from_file_location("kd_build_search", ruta)  # describe cómo cargar el archivo
    modulo = importlib.util.module_from_spec(spec)  # crea un módulo vacío a partir de esa descripción
    with contextlib.redirect_stdout(io.StringIO()):  # mientras se ejecuta, los print() se descartan
        spec.loader.exec_module(modulo)  # ejecuta el archivo y llena el módulo
    return modulo                      # devolvemos el módulo con build_kd_tree y search_kd_tree


def crear_sensor_kdtree(puntos):
    """Construye el KD-Tree con `puntos` y devuelve su función de búsqueda por rango."""
    modulo = cargar_modulo_kdtree()    # cargamos el código del KD-Tree
    if modulo is None:                 # si no se encontró el archivo...
        raise FileNotFoundError("No se encontró KD-Tree/Build&Search.py")  # ...lanzamos un error claro

    raiz = modulo.build_kd_tree(list(puntos))  # construimos el árbol con todos los puntos
    return lambda rango: modulo.search_kd_tree(raiz, rango)  # función que busca en ese árbol


# ---------------------------------------------------------------------------
# 3. Laberintos en texto (mismo formato que fuerzabruta.py)
# ---------------------------------------------------------------------------
#   #  pared      .  camino libre      M  inicio del ratón      E  salida

@dataclass                             # clase de datos: guarda el laberinto ya interpretado
class Laberinto:
    paredes: set                       # coordenadas (x, y) de todas las paredes
    libres: set                        # coordenadas (x, y) de las celdas transitables
    inicio: tuple                      # posición de la 'M'
    meta: tuple                        # posición de la 'E'
    ancho: int                         # número de columnas
    alto: int                          # número de filas


def leer_laberinto(lineas):
    """
    Convierte una lista de strings en un Laberinto.
    Las filas más cortas se completan con pared (el laberinto de ejemplo de
    fuerzabruta.py tiene filas de distinto largo).
    """
    alto = len(lineas)                 # número de filas = cantidad de strings
    ancho = max(len(linea) for linea in lineas)  # ancho = la fila más larga
    paredes, libres = set(), set()     # conjuntos vacíos para clasificar las celdas
    inicio = meta = None               # aún no sabemos dónde están M y E

    for y in range(alto):              # recorremos cada fila
        for x in range(ancho):         # recorremos cada columna
            c = lineas[y][x] if x < len(lineas[y]) else "#"  # si la fila es corta, rellena con pared
            if c in ".ME":             # '.', 'M' y 'E' son celdas transitables
                libres.add((x, y))     # la registramos como libre
                if c == "M":           # ¿es el inicio?
                    inicio = (x, y)    # guardamos la posición inicial
                elif c == "E":         # ¿es la salida?
                    meta = (x, y)      # guardamos la posición de la meta
            else:                      # cualquier otro carácter se trata como pared
                paredes.add((x, y))    # la registramos como pared

    return Laberinto(paredes, libres, inicio, meta, ancho, alto)  # empaquetamos todo


def dibujar_camino(lineas, camino):
    """Devuelve el laberinto en texto marcando el camino con '*'."""
    ancho = max(len(linea) for linea in lineas)  # ancho de la fila más larga
    filas = [list(linea.ljust(ancho, "#")) for linea in lineas]  # filas como listas, rellenas con pared
    for x, y in camino:                # recorremos cada celda del camino
        if filas[y][x] == ".":         # solo marcamos celdas libres (respeta 'M' y 'E')
            filas[y][x] = "*"          # ponemos el asterisco del camino
    return ["".join(f) for f in filas]  # volvemos a convertir cada fila en string


# ---------------------------------------------------------------------------
# 4. Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":             # solo corre al ejecutar este archivo directamente
    laberinto_texto = [                # laberinto de ejemplo
        "#####",
        "#M..#",
        "#.#.###",
        "#.#..E#",
        "#######",
    ]

    lab = leer_laberinto(laberinto_texto)  # interpretamos el texto
    print("Laberinto:")                # título
    print("\n".join(laberinto_texto))  # mostramos el laberinto original

    # Mismo BFS, tres formas distintas de "sentir" el laberinto
    sensores = {                       # diccionario: nombre -> función de vecinos
        "Fuerza bruta (celdas libres)": vecinos_desde_libres(  # sensor sobre celdas libres
            crear_sensor_fuerza_bruta(lab.libres)
        ),
        "Fuerza bruta (paredes)": vecinos_desde_paredes(  # sensor sobre paredes
            crear_sensor_fuerza_bruta(lab.paredes), lab.ancho, lab.alto
        ),
    }
    try:                               # el KD-Tree es opcional: puede no estar el archivo
        sensores["KD-Tree (celdas libres)"] = vecinos_desde_libres(  # sensor KD-Tree
            crear_sensor_kdtree(lab.libres)
        )
    except FileNotFoundError:          # si no existe Build&Search.py...
        pass                           # ...simplemente se omite ese sensor

    for nombre, vecinos in sensores.items():  # probamos el BFS con cada sensor
        r = bfs(lab.inicio, lab.meta, vecinos)  # ejecutamos la búsqueda
        print(f"\n[{nombre}]")         # nombre del sensor usado
        print("Encontrado:", r.encontrado, "| Pasos:", r.pasos,  # resumen del resultado
              "| Explorados:", len(r.explorados))
        print("Camino:", r.camino)     # lista de celdas del camino

    print("\nCamino marcado con '*':")  # título de la vista gráfica en texto
    resultado = bfs(lab.inicio, lab.meta, list(sensores.values())[0])  # BFS con el primer sensor
    print("\n".join(dibujar_camino(laberinto_texto, resultado.camino)))  # laberinto con el camino
