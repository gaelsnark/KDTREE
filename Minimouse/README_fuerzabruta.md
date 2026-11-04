
# MiniMouse - Fuerza Bruta

## Descripción
Este programa forma parte del proyecto MiniMouse, basado
en el tema Orthogonal Range Searching.

El objetivo es detectar las paredes que se encuentran
cerca del robot dentro de un laberinto.

## Funcionamiento
1. Creamos un laberinto utilizando una matriz.
2. Identificamos las paredes mediante coordenadas (x, y).
3. Revisamos todas las paredes utilizando fuerza bruta.
4. Detectamos las paredes dentro del alcance del sensor.

## Archivos
- fuerzabruta.py: contiene el algoritmo de fuerza bruta.

- test_fuerzabruta.py: contiene las pruebas unitarias.

## Lenguaje
Python 3.14.2

## Ejecutar el programa
Desde la carpeta principal del repositorio:

    python Minimouse/fuerzabruta.py

## Ejecutar las pruebas

    python Minimouse/test_fuerzabruta.py


## Resultados de las pruebas

Se realizaron tres pruebas unitarias:

1. Detectar una pared dentro del rango.
2. Comprobar que no se detecten paredes fuera del rango.
3. Verificar el funcionamiento del sensor del robot.

Las tres pruebas se ejecutaron correctamente.

## Ejemplo de funcionamiento

Posicion del robot: (1, 1)
Alcance del sensor: 1 casilla

Paredes cercanas:
[(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (2, 2)]

Total de paredes detectadas: 6

## Complejidad
El algoritmo tiene una complejidad O(n), porque revisa
todas las paredes del laberinto para encontrar las que
se encuentran dentro del rango seleccionado.

## Relacion con KD-Tree

La fuerza bruta funciona como nuestro algoritmo base,
ya que revisa todas las paredes del laberinto.

Posteriormente, compararemos sus resultados con KD-Tree,
que organiza los puntos mediante un arbol binario para
evitar revisar zonas innecesarias.

Ambos algoritmos deberan detectar las mismas paredes.

## Estado
Fuerza bruta implementada y pruebas unitarias realizadas.

## Responsable
Ana Emilia Rubalcava González
