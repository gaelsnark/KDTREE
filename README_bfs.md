# MiniMouse - BFS (Breadth-First Search)

## Descripción
El ratón busca la salida del laberinto con una búsqueda en anchura (BFS).
BFS expande las celdas por capas de distancia, por lo que el primer camino
que llega a la meta es siempre el **más corto** en número de pasos.

## Cómo se conecta con el resto del proyecto
El BFS no depende de cómo se guarde el laberinto. Solo necesita una función
`obtener_vecinos(celda)`, que se construye a partir de un sensor de búsqueda
por rango ortogonal:

| Sensor | Archivo | Puntos que guarda |
|---|---|---|
| KD-Tree | `KD-Tree/Build&Search.py` | celdas libres |
| Fuerza bruta | `fuerzabruta.py` | paredes (o celdas libres) |

Para cada celda se consulta la caja 3x3 que la rodea (`R = ((x-1,x+1),(y-1,y+1))`)
y se conservan los 4 vecinos ortogonales (arriba, derecha, abajo, izquierda).

Convención de coordenadas: `(x, y) = (columna, fila)`.

## Archivos
- `bfs.py`: algoritmo BFS, adaptadores de sensor y lector de laberintos en texto.
- `test_bfs.py`: pruebas unitarias.
- `../interfaz_bfs.py`: interfaz con botón "Resolver con BFS" y animación (usa `interfaz.py` sin modificarlo).

## Ejecutar
    python Minimouse/bfs.py          # demo en consola
    python Minimouse/test_bfs.py     # pruebas (desde la raíz del repo)
    python interfaz_bfs.py           # interfaz gráfica con BFS

## Interfaz gráfica
- Azul: celdas exploradas por BFS (en el orden en que se descubren).
- Dorado: camino más corto, recorrido por el ratón.
- Se puede elegir el sensor (KD-Tree o fuerza bruta) y se muestra el número
  de consultas al sensor, para comparar ambos métodos.

## Pruebas
1. Laberinto simple con camino conocido.
2. Laberinto sin salida.
3. Inicio igual a la meta.
4. Elige el camino corto cuando existe uno largo.
5. El sensor de paredes respeta los límites.
6. Camino válido y óptimo en 60 laberintos aleatorios (comparado contra un
   cálculo de distancia independiente).
7. Sensor de paredes y de celdas libres dan el mismo resultado.
8. KD-Tree y fuerza bruta producen exactamente el mismo BFS.
9. El contador de consultas funciona.

## Complejidad
BFS expande cada celda a lo sumo una vez: V consultas al sensor (V = celdas libres).

- Con fuerza bruta cada consulta es O(n) -> O(V·n) en total.
- Con KD-Tree cada consulta es O(√n + k) -> O(V·(√n + k)) en total.
