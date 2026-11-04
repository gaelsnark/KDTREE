
import unittest
from fuerzabruta import fuerzaBruta, detectarParedes

# Probar nuestro algoritmo de fuerza bruta
class testFuerzaBruta(unittest.TestCase):

    # Prueba 1: Verificamos que encuentre las paredes dentro del rango
    def test_pared_dentro(self):
        paredes = [(1, 1), (5, 5)]

        # Buscamos paredes dentro del rectangulo de (0,0) a (2,2)
        resultado = fuerzaBruta(paredes, 0, 2, 0, 2)

        # Comprobamos que solo encuentre la pared (1,1)
        self.assertEqual(resultado, [(1, 1)])

    # Prueba 2: Verificamos que no encuentre paredes fuera del rango
    def test_sin_resultados(self):
        paredes = [(5, 5), (6, 6)]

        # Buscamos en una zona donde no hay paredes
        resultado = fuerzaBruta(paredes, 0, 2, 0, 2)

        # El resultado debe ser una lista vacia
        self.assertEqual(resultado, [])

    # Prueba 3: Comprobamos que funcione el sensor del MiniMouse
    def test_sensor(self):
        paredes = [(0, 0), (2, 2), (5, 5)]

        # Colocamos al robot en (1,1) con alcance de 1 casilla
        resultado = detectarParedes(paredes, 1, 1, 1)

        # Debe detectar las paredes (0,0) y (2,2)
        self.assertEqual(resultado, [(0, 0), (2, 2)])


# Ejecutamos las pruebas cuando abrimos este archivo directamente
if __name__ == "__main__":
    unittest.main()
