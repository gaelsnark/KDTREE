import random                          # para generar laberintos aleatorios reproducibles
import unittest                        # framework de pruebas de Python

from bfs import (                      # importamos todo lo que vamos a probar
    DIRECCIONES,                       # los 4 movimientos ortogonales
    SensorConContador,                 # sensor que cuenta consultas
    bfs,                               # el algoritmo principal
    cargar_modulo_kdtree,              # para saber si existe el KD-Tree
    crear_sensor_fuerza_bruta,         # sensor de fuerza bruta
    crear_sensor_kdtree,               # sensor KD-Tree
    leer_laberinto,                    # convierte texto en laberinto
    vecinos_desde_libres,              # vecinos a partir de celdas libres
    vecinos_desde_paredes,             # vecinos a partir de paredes
)


def laberinto_aleatorio(ancho, alto, densidad, semilla):
    """Crea un laberinto aleatorio (inicio arriba-izq, meta abajo-der)."""
    rnd = random.Random(semilla)       # generador con semilla: mismo resultado cada vez
    libres = {                         # conjunto de celdas transitables
        (x, y)                         # cada celda es una coordenada (x, y)
        for x in range(ancho)          # recorre todas las columnas
        for y in range(alto)           # recorre todas las filas
        if rnd.random() > densidad     # la celda es libre si NO cae en la fracción de paredes
    }
    inicio, meta = (0, 0), (ancho - 1, alto - 1)  # esquinas opuestas
    libres |= {inicio, meta}           # garantizamos que inicio y meta sean libres
    return libres, inicio, meta        # devolvemos el laberinto generado


def distancia_referencia(libres, inicio, meta):
    """
    Distancia mínima calculada de forma INDEPENDIENTE al BFS (relajación
    repetida tipo Bellman-Ford). Sirve para comprobar que BFS es óptimo.
    """
    inf = float("inf")                 # infinito: "aún no alcanzable"
    dist = {c: inf for c in libres}    # distancia inicial infinita para todas las celdas
    dist[inicio] = 0                   # el inicio está a distancia 0
    cambio = True                      # bandera: ¿se mejoró alguna distancia?
    while cambio:                      # repetimos hasta que nada mejore
        cambio = False                 # asumimos que esta vuelta no cambiará nada
        for (x, y) in libres:          # revisamos cada celda libre
            for dx, dy in DIRECCIONES: # y cada uno de sus 4 vecinos
                v = (x + dx, y + dy)   # coordenada del vecino
                if v in dist and dist[v] + 1 < dist[(x, y)]:  # ¿pasar por el vecino acorta el camino?
                    dist[(x, y)] = dist[v] + 1  # sí: actualizamos la distancia
                    cambio = True      # hubo mejora, hay que repetir
    return None if dist[meta] == inf else dist[meta]  # None si la meta es inalcanzable


def camino_valido(camino, libres, inicio, meta):
    if not camino or camino[0] != inicio or camino[-1] != meta:  # debe empezar y terminar bien
        return False                   # extremos incorrectos: camino inválido
    if any(c not in libres for c in camino):  # ninguna celda puede ser pared
        return False                   # atravesó una pared: inválido
    return all(                        # cada paso debe ser a una celda contigua
        abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1  # distancia de Manhattan = 1 entre celdas consecutivas
        for a, b in zip(camino, camino[1:])  # pares de celdas consecutivas
    )


class TestBFS(unittest.TestCase):      # agrupa todas las pruebas del BFS

    # Prueba 1: laberinto simple con camino conocido
    def test_laberinto_simple(self):
        lab = leer_laberinto([         # laberinto de ejemplo con salida 'E'
            "#####",
            "#M..#",
            "#.#.###",
            "#.#..E#",
            "#######",
        ])
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(lab.libres))  # función de vecinos
        r = bfs(lab.inicio, lab.meta, vecinos)  # ejecutamos BFS

        self.assertTrue(r.encontrado)  # debe encontrar la salida
        self.assertEqual(              # el camino debe ser exactamente este
            r.camino,
            [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (4, 3), (5, 3)],
        )
        self.assertEqual(r.pasos, 6)   # 7 celdas = 6 pasos

    # Prueba 2: laberinto sin salida
    def test_sin_salida(self):
        lab = leer_laberinto([         # una pared '#' separa a M de E
            "#######",
            "#M.#.E#",
            "#######",
        ])
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(lab.libres))  # función de vecinos
        r = bfs(lab.inicio, lab.meta, vecinos)  # ejecutamos BFS

        self.assertFalse(r.encontrado)  # no debe encontrar salida
        self.assertEqual(r.camino, [])  # el camino debe estar vacío
        self.assertIsNone(r.pasos)     # los pasos deben ser None

    # Prueba 3: el ratón ya está en la salida
    def test_inicio_es_meta(self):
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta({(1, 1)}))  # laberinto de una sola celda
        r = bfs((1, 1), (1, 1), vecinos)  # inicio y meta coinciden

        self.assertTrue(r.encontrado)  # se considera encontrada
        self.assertEqual(r.camino, [(1, 1)])  # el camino es solo esa celda
        self.assertEqual(r.pasos, 0)   # cero pasos

    # Prueba 4: BFS elige el camino más corto cuando hay uno largo y uno corto
    def test_elige_camino_mas_corto(self):
        lab = leer_laberinto([         # hay un camino directo y otro por abajo
            "#######",
            "#M...E#",
            "#.###.#",
            "#.....#",
            "#######",
        ])
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(lab.libres))  # función de vecinos
        r = bfs(lab.inicio, lab.meta, vecinos)  # ejecutamos BFS

        self.assertEqual(r.pasos, 4)   # debe tomar el directo (4 pasos), no el de abajo (8)

    # Prueba 5: nunca atraviesa paredes ni sale del laberinto (sensor de paredes)
    def test_sensor_de_paredes_respeta_limites(self):
        lab = leer_laberinto([         # laberinto sin paredes, de 2x2
            "M.",
            ".E",
        ])
        vecinos = vecinos_desde_paredes(  # sensor basado en paredes (con límites)
            crear_sensor_fuerza_bruta(lab.paredes), lab.ancho, lab.alto
        )
        self.assertEqual(sorted(vecinos((0, 0))), [(0, 1), (1, 0)])  # en la esquina solo hay 2 vecinos

    # Prueba 6: el camino es válido y óptimo en muchos laberintos aleatorios
    def test_optimo_en_laberintos_aleatorios(self):
        for semilla in range(60):      # 60 laberintos distintos
            libres, inicio, meta = laberinto_aleatorio(8, 8, 0.3, semilla)  # generamos uno de 8x8
            vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(libres))  # función de vecinos
            r = bfs(inicio, meta, vecinos)  # ejecutamos BFS

            esperado = distancia_referencia(libres, inicio, meta)  # distancia por método independiente
            if esperado is None:       # si la meta es inalcanzable...
                self.assertFalse(r.encontrado, f"semilla {semilla}")  # ...BFS no debe encontrarla
            else:                      # si es alcanzable...
                self.assertTrue(r.encontrado, f"semilla {semilla}")  # ...BFS debe encontrarla
                self.assertEqual(r.pasos, esperado, f"semilla {semilla}")  # ...con la distancia mínima
                self.assertTrue(camino_valido(r.camino, libres, inicio, meta))  # ...y un camino válido

    # Prueba 7: sensor de paredes y de celdas libres dan el mismo resultado
    def test_sensores_equivalentes(self):
        for semilla in range(30):      # 30 laberintos distintos
            libres, inicio, meta = laberinto_aleatorio(8, 8, 0.3, semilla)  # generamos uno de 8x8
            paredes = {                # las paredes son las celdas que NO son libres
                (x, y) for x in range(8) for y in range(8) if (x, y) not in libres
            }
            r1 = bfs(inicio, meta,     # BFS usando el sensor de celdas libres
                     vecinos_desde_libres(crear_sensor_fuerza_bruta(libres)))
            r2 = bfs(inicio, meta,     # BFS usando el sensor de paredes
                     vecinos_desde_paredes(crear_sensor_fuerza_bruta(paredes), 8, 8))
            self.assertEqual(r1.camino, r2.camino, f"semilla {semilla}")  # deben coincidir

    # Prueba 8: KD-Tree y fuerza bruta producen exactamente el mismo BFS
    @unittest.skipIf(cargar_modulo_kdtree() is None, "KD-Tree/Build&Search.py no encontrado")  # se omite si falta el KD-Tree
    def test_kdtree_igual_que_fuerza_bruta(self):
        for semilla in range(30):      # 30 laberintos distintos
            libres, inicio, meta = laberinto_aleatorio(10, 10, 0.3, semilla)  # generamos uno de 10x10
            r_fb = bfs(inicio, meta,   # BFS con fuerza bruta
                       vecinos_desde_libres(crear_sensor_fuerza_bruta(libres)))
            r_kd = bfs(inicio, meta,   # BFS con KD-Tree
                       vecinos_desde_libres(crear_sensor_kdtree(libres)))
            self.assertEqual(r_fb.camino, r_kd.camino, f"semilla {semilla}")  # mismo camino
            self.assertEqual(r_fb.explorados, r_kd.explorados, f"semilla {semilla}")  # mismo orden de exploración

    # Prueba 9: el contador registra una consulta por celda expandida
    def test_contador_de_consultas(self):
        lab = leer_laberinto(["M.E"])  # pasillo de 3 celdas
        sensor = SensorConContador(crear_sensor_fuerza_bruta(lab.libres))  # sensor con contador
        r = bfs(lab.inicio, lab.meta, vecinos_desde_libres(sensor))  # ejecutamos BFS

        self.assertTrue(r.encontrado)  # debe encontrar la salida
        # Se expande (0,0) y (1,0); al descubrir la meta se detiene
        self.assertEqual(sensor.consultas, 2)  # solo 2 consultas al sensor


if __name__ == "__main__":             # solo corre al ejecutar este archivo directamente
    unittest.main()                    # lanza todas las pruebas
