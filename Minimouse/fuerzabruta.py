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

#