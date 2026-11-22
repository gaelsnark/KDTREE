import random
import unittest

from bfs import (
    DIRECCIONES,
    SensorConContador,
    bfs,
    cargar_modulo_kdtree,
    crear_sensor_fuerza_bruta,
    crear_sensor_kdtree,
    leer_laberinto,
    vecinos_desde_libres,
    vecinos_desde_paredes,
)


def laberinto_aleatorio(ancho, alto, densidad, semilla):
    """Crea un laberinto aleatorio (inicio arriba-izq, meta abajo-der)."""
    rnd = random.Random(semilla)
    libres = {
        (x, y)
        for x in range(ancho)
        for y in range(alto)
        if rnd.random() > densidad
    }
    inicio, meta = (0, 0), (ancho - 1, alto - 1)
    libres |= {inicio, meta}
    return libres, inicio, meta


def distancia_referencia(libres, inicio, meta):
    """
    Distancia mínima calculada de forma INDEPENDIENTE al BFS (relajación
    repetida tipo Bellman-Ford). Sirve para comprobar que BFS es óptimo.
    """
    inf = float("inf")
    dist = {c: inf for c in libres}
    dist[inicio] = 0
    cambio = True
    while cambio:
        cambio = False
        for (x, y) in libres:
            for dx, dy in DIRECCIONES:
                v = (x + dx, y + dy)
                if v in dist and dist[v] + 1 < dist[(x, y)]:
                    dist[(x, y)] = dist[v] + 1
                    cambio = True
    return None if dist[meta] == inf else dist[meta]


def camino_valido(camino, libres, inicio, meta):
    if not camino or camino[0] != inicio or camino[-1] != meta:
        return False
    if any(c not in libres for c in camino):
        return False
    return all(
        abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
        for a, b in zip(camino, camino[1:])
    )


class TestBFS(unittest.TestCase):

    # Prueba 1: laberinto simple con camino conocido
    def test_laberinto_simple(self):
        lab = leer_laberinto([
            "#####",
            "#M..#",
            "#.#.###",
            "#.#..E#",
            "#######",
        ])
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(lab.libres))
        r = bfs(lab.inicio, lab.meta, vecinos)

        self.assertTrue(r.encontrado)
        self.assertEqual(
            r.camino,
            [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (4, 3), (5, 3)],
        )
        self.assertEqual(r.pasos, 6)

    # Prueba 2: laberinto sin salida
    def test_sin_salida(self):
        lab = leer_laberinto([
            "#######",
            "#M.#.E#",
            "#######",
        ])
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(lab.libres))
        r = bfs(lab.inicio, lab.meta, vecinos)

        self.assertFalse(r.encontrado)
        self.assertEqual(r.camino, [])
        self.assertIsNone(r.pasos)

    # Prueba 3: el ratón ya está en la salida
    def test_inicio_es_meta(self):
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta({(1, 1)}))
        r = bfs((1, 1), (1, 1), vecinos)

        self.assertTrue(r.encontrado)
        self.assertEqual(r.camino, [(1, 1)])
        self.assertEqual(r.pasos, 0)

    # Prueba 4: BFS elige el camino más corto cuando hay uno largo y uno corto
    def test_elige_camino_mas_corto(self):
        lab = leer_laberinto([
            "#######",
            "#M...E#",
            "#.###.#",
            "#.....#",
            "#######",
        ])
        vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(lab.libres))
        r = bfs(lab.inicio, lab.meta, vecinos)

        self.assertEqual(r.pasos, 4)

    # Prueba 5: nunca atraviesa paredes ni sale del laberinto (sensor de paredes)
    def test_sensor_de_paredes_respeta_limites(self):
        lab = leer_laberinto([
            "M.",
            ".E",
        ])
        vecinos = vecinos_desde_paredes(
            crear_sensor_fuerza_bruta(lab.paredes), lab.ancho, lab.alto
        )
        self.assertEqual(sorted(vecinos((0, 0))), [(0, 1), (1, 0)])

    # Prueba 6: el camino es válido y óptimo en muchos laberintos aleatorios
    def test_optimo_en_laberintos_aleatorios(self):
        for semilla in range(60):
            libres, inicio, meta = laberinto_aleatorio(8, 8, 0.3, semilla)
            vecinos = vecinos_desde_libres(crear_sensor_fuerza_bruta(libres))
            r = bfs(inicio, meta, vecinos)

            esperado = distancia_referencia(libres, inicio, meta)
            if esperado is None:
                self.assertFalse(r.encontrado, f"semilla {semilla}")
            else:
                self.assertTrue(r.encontrado, f"semilla {semilla}")
                self.assertEqual(r.pasos, esperado, f"semilla {semilla}")
                self.assertTrue(camino_valido(r.camino, libres, inicio, meta))

    # Prueba 7: sensor de paredes y de celdas libres dan el mismo resultado
    def test_sensores_equivalentes(self):
        for semilla in range(30):
            libres, inicio, meta = laberinto_aleatorio(8, 8, 0.3, semilla)
            paredes = {
                (x, y) for x in range(8) for y in range(8) if (x, y) not in libres
            }
            r1 = bfs(inicio, meta,
                     vecinos_desde_libres(crear_sensor_fuerza_bruta(libres)))
            r2 = bfs(inicio, meta,
                     vecinos_desde_paredes(crear_sensor_fuerza_bruta(paredes), 8, 8))
            self.assertEqual(r1.camino, r2.camino, f"semilla {semilla}")

    # Prueba 8: KD-Tree y fuerza bruta producen exactamente el mismo BFS
    @unittest.skipIf(cargar_modulo_kdtree() is None, "KD-Tree/Build&Search.py no encontrado")
    def test_kdtree_igual_que_fuerza_bruta(self):
        for semilla in range(30):
            libres, inicio, meta = laberinto_aleatorio(10, 10, 0.3, semilla)
            r_fb = bfs(inicio, meta,
                       vecinos_desde_libres(crear_sensor_fuerza_bruta(libres)))
            r_kd = bfs(inicio, meta,
                       vecinos_desde_libres(crear_sensor_kdtree(libres)))
            self.assertEqual(r_fb.camino, r_kd.camino, f"semilla {semilla}")
            self.assertEqual(r_fb.explorados, r_kd.explorados, f"semilla {semilla}")

    # Prueba 9: el contador registra una consulta por celda expandida
    def test_contador_de_consultas(self):
        lab = leer_laberinto(["M.E"])
        sensor = SensorConContador(crear_sensor_fuerza_bruta(lab.libres))
        r = bfs(lab.inicio, lab.meta, vecinos_desde_libres(sensor))

        self.assertTrue(r.encontrado)
        # Se expande (0,0) y (1,0); al descubrir la meta se detiene
        self.assertEqual(sensor.consultas, 2)


if __name__ == "__main__":
    unittest.main()
