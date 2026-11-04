#Responsable Ana Rubalcava
#Fuerza bruta para Minimouse

# 1 Crear un laberinto sencillo
# Representación de nuestro laberinto
# # -> pared
# M = posición inicial de nuestro ratón
# . = camino libre

laberinto = [
    "#####",
    "#M..#",
    "#.#.###",
    "#.#...#",
    "#######",
]

#Recorrer las filas para mostrar el laberinto    
for fila in laberinto:
    print(fila)

# 2 Función para identificar las paredes del laberinto

def obtenerParedes (laberinto):
    #crear la lista vacía donde se iran guardando las paredes
    paredes = []

    #recorre las filas y obtiene su posición Y.
    for y, fila in enumerate(laberinto):
        #recorre las columnas y obtiene su posición X
        for x, casilla in enumerate(fila):
            #checa si encontramos una pared
            if casilla == "#":
                #guarda las coordenadas de esa pared
                paredes.append((x,y))
    return paredes

#Prueba para verificar las paredes
paredes = obtenerParedes(laberinto)

print("\nCoordenadas de las paredes:")
print(paredes)
print("Total de paredes:", len(paredes))


#Algoritmo Fuerza Bruta
#Busca las paredes dentro de una zona rectangular 
#Recibe las paredes y los cuatro límites del área que queremos revisar
def fuerzaBruta(paredes, xmin, xmax, ymin, ymax):
    #crea una lista vacía para guardar las paredes detectadas
    encontradas = []

    #revisa una por una todas las paredes
    for x, y in paredes:
        #comprueba si la pared se encuentra dentro dle rectángulo
        if xmin <= x <= xmax and ymin <= y <= ymax:
            #guarda las paredes que cumplen la condición
            encontradas.append((x,y))

    return encontradas

#Probar el  algoritmo de fuerza bruta 
resultado = fuerzaBruta(paredes, 0, 2, 0,2)

print("\nParedes dentro del rango:")
print(resultado)
print("Total de paredes detectadas:", len(resultado))

# 3 Simular el sensor del MiniMouse

# robot_x y robot_y = indican dónde está nuestro robot
def detectarParedes(paredes, robot_x, robot_y, alcance):
    #alcance = indica cuántas casillas alcanza a revisar el sensor
    #xmin, xmax, ymin, ymax = definen el réctangulo de búsqueda
    xmin = robot_x - alcance
    xmax = robot_x + alcance
    ymin = robot_y - alcance
    ymax = robot_y + alcance

    resultado = fuerzaBruta(paredes, xmin, xmax, ymin, ymax)

    return resultado


# Prueba del sensor del MiniMouse

robot_x = 1
robot_y = 1
alcance = 1

paredes_cercanas = detectarParedes(
    paredes, robot_x, robot_y, alcance
)

print("\nDETECCIÓN DE OBSTACULOS:")
print("Posición del robot:", (robot_x, robot_y))
print("Alcance del sensor:", alcance)
print("Paredes cercanas:", paredes_cercanas)
print("Total detectadas:", len(paredes_cercanas))


