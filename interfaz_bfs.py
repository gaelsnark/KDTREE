# Interfaz con BFS para MiniMouse
# Reutiliza el laberinto y el ratón de interfaz.py SIN modificarlo:
# MazeSolverBFS hereda de MazeSolver y le agrega la búsqueda BFS.
#
# Ejecutar desde la raíz del repositorio:
#     python interfaz_bfs.py

import tkinter as tk                   # librería gráfica de Python
import time                            # para medir cuánto tarda el BFS

from interfaz import (                 # reutilizamos lo que ya existe en interfaz.py
    MazeSolver, cell_size, start,      # clase base, tamaño de celda y posición inicial
    easy_grid_size, medium_grid_size, hard_grid_size,  # tamaños de los 3 niveles
)
from Minimouse.bfs import (            # importamos nuestro módulo BFS
    SensorConContador,                 # sensor que cuenta consultas
    bfs,                               # el algoritmo de búsqueda
    crear_sensor_fuerza_bruta,         # sensor de fuerza bruta
    crear_sensor_kdtree,               # sensor KD-Tree
    vecinos_desde_libres,              # convierte un sensor en función de vecinos
)

#Velocidad de la animación (milisegundos entre cada paso)
explore_delay = 25                     # pausa al pintar cada celda explorada
walk_delay = 70                        # pausa entre cada paso del ratón

#root = ventana actual (igual que en interfaz.py)
root = None                            # se asigna al abrir la ventana


class MazeSolverBFS(MazeSolver):       # hereda el laberinto y el ratón de MazeSolver
    # Nota: el BFS trabaja con (x, y) = (columna, fila), igual que el KD-Tree.
    # El grid y player_position usan [fila][columna], por eso se convierte.

    def __init__(self, master, grid_size):
        #Crea el laberinto, el canvas y el ratón con el código original
        super().__init__(master, grid_size)  # ejecuta el __init__ de MazeSolver

        #Estado de la animación BFS
        self.animating = False         # True mientras se está animando
        self.after_id = None           # id de la próxima acción programada (para cancelarla)

        self.create_controls()         # agrega los botones debajo del canvas

    def create_controls(self):
        #Panel con los botones y la selección del sensor
        panel = tk.Frame(self.master)  # contenedor para alinear los controles
        panel.pack(pady=5)             # lo coloca bajo el canvas con margen vertical

        self.btn_bfs = tk.Button(panel, text="Resolver con BFS", command=self.solve_bfs)  # botón que lanza el BFS
        self.btn_bfs.grid(row=0, column=0, padx=5)  # columna 0 del panel

        self.btn_new = tk.Button(panel, text="Nuevo laberinto", command=self.new_maze)  # botón que regenera el laberinto
        self.btn_new.grid(row=0, column=1, padx=5)  # columna 1 del panel

        #Sensor que usa el ratón para "ver" sus vecinos
        self.sensor_var = tk.StringVar(value="KD-Tree")  # guarda la opción elegida (KD-Tree por defecto)
        tk.Radiobutton(panel, text="KD-Tree", variable=self.sensor_var,  # opción KD-Tree
                       value="KD-Tree").grid(row=0, column=2)
        tk.Radiobutton(panel, text="Fuerza bruta", variable=self.sensor_var,  # opción fuerza bruta
                       value="Fuerza bruta").grid(row=0, column=3)

        self.status = tk.Label(self.master, text="Presiona 'Resolver con BFS'",  # texto de estado inicial
                               font=("Times New Roman", 11))
        self.status.pack(pady=(0, 8))  # lo coloca debajo de los botones

    def build_neighbors_function(self):
        #Puntos del KD-Tree = celdas libres del laberinto, como (x, y)
        free_cells = [                 # lista de todas las celdas transitables
            (x, y)                     # (columna, fila)
            for y in range(self.grid_size)  # recorre filas
            for x in range(self.grid_size)  # recorre columnas
            if self.grid[y][x] == 0    # 0 = camino libre (1 = pared)
        ]

        sensor_name = self.sensor_var.get()  # lee qué sensor eligió el usuario
        if sensor_name == "KD-Tree":   # si eligió KD-Tree...
            try:                       # ...intentamos construirlo
                search = crear_sensor_kdtree(free_cells)  # árbol con las celdas libres
            except FileNotFoundError:  # si falta KD-Tree/Build&Search.py
                #Si no está KD-Tree/Build&Search.py usamos fuerza bruta
                sensor_name = "Fuerza bruta"  # cambiamos el nombre mostrado
                self.sensor_var.set(sensor_name)  # actualizamos el botón de opción
                search = crear_sensor_fuerza_bruta(free_cells)  # sensor alternativo
        else:                          # si eligió fuerza bruta
            search = crear_sensor_fuerza_bruta(free_cells)  # sensor de fuerza bruta

        self.sensor = SensorConContador(search)  # envolvemos el sensor para contar consultas
        self.sensor_name = sensor_name  # guardamos el nombre para mostrarlo al final
        return vecinos_desde_libres(self.sensor)  # función de vecinos que usará el BFS

    def solve_bfs(self):
        if self.animating:             # si ya hay una animación corriendo...
            return                     # ...no iniciamos otra

        self.clear_search()            # limpia cualquier recorrido anterior

        neighbors = self.build_neighbors_function()  # prepara el sensor y los vecinos
        start_xy = (start[1], start[0])  # inicio convertido de (fila, col) a (x, y)
        end_xy = (self.end[1], self.end[0])  # meta convertida de (fila, col) a (x, y)

        #Se calcula el BFS completo y después se anima paso a paso
        t0 = time.perf_counter()       # marca de tiempo antes del BFS
        self.result = bfs(start_xy, end_xy, neighbors)  # ejecuta la búsqueda
        self.elapsed_ms = (time.perf_counter() - t0) * 1000  # tiempo transcurrido en milisegundos

        if not self.result.encontrado:  # si no hay camino a la meta...
            self.status.config(text="No existe camino hasta la salida")  # ...lo informamos
            return                     # ...y terminamos

        self.animating = True          # marcamos que empieza la animación
        self.btn_bfs.config(state="disabled")  # bloqueamos el botón mientras anima
        self.status.config(text="Explorando con BFS...")  # mensaje de progreso
        self.animate_exploration(0)    # arrancamos con la primera celda explorada

    def paint_cell(self, x, y, color, tag):
        #No se pinta sobre el inicio ni la meta para conservar sus colores
        if (y, x) == start or (y, x) == self.end:  # (fila, col) coincide con inicio o meta
            return                     # no pintamos encima
        self.canvas.create_rectangle(  # dibuja un cuadrado en la celda
            x * cell_size, y * cell_size,  # esquina superior izquierda en píxeles
            (x + 1) * cell_size, (y + 1) * cell_size,  # esquina inferior derecha en píxeles
            fill=color, outline="gray", tags=tag  # color de relleno, borde y etiqueta para borrarlo luego
        )

    def animate_exploration(self, i):
        #Pinta de azul las celdas en el orden en que BFS las descubre
        explored = self.result.explorados  # lista de celdas en orden de descubrimiento

        if i < len(explored):          # si aún quedan celdas por pintar
            x, y = explored[i]         # tomamos la i-ésima celda
            self.paint_cell(x, y, "lightblue", "explorado")  # la pintamos de azul claro
            self.canvas.tag_raise("player")  # mantenemos el ratón visible encima
            self.after_id = self.master.after(explore_delay, self.animate_exploration, i + 1)  # programa la siguiente celda
        else:                          # ya se pintaron todas las celdas exploradas
            self.status.config(text="Salida encontrada, el ratón sigue el camino más corto...")  # mensaje de progreso
            self.after_id = self.master.after(300, self.animate_walk, 0)  # tras una pausa, el ratón empieza a caminar

    def animate_walk(self, i):
        #El ratón recorre el camino más corto, dejando un rastro dorado
        path = self.result.camino      # camino más corto de inicio a meta

        if i < len(path):              # si el ratón aún no llega al final
            x, y = path[i]             # i-ésima celda del camino
            self.paint_cell(x, y, "gold", "camino")  # deja rastro dorado
            self.player_position = [y, x]  # mueve al ratón (guardado como [fila, col])
            self.draw_player()         # redibuja al ratón en su nueva posición
            self.after_id = self.master.after(walk_delay, self.animate_walk, i + 1)  # programa el siguiente paso
        else:                          # el ratón llegó a la meta
            self.animating = False     # termina la animación
            self.btn_bfs.config(state="normal")  # reactiva el botón
            self.status.config(text=(  # muestra el resumen final
                f"¡Salida encontrada! {self.result.pasos} pasos | "  # pasos del camino más corto
                f"{len(self.result.explorados)} celdas exploradas | "  # celdas que BFS tuvo que descubrir
                f"{self.sensor.consultas} consultas ({self.sensor_name}) | "  # consultas hechas al sensor
                f"{self.elapsed_ms:.2f} ms"  # tiempo del BFS
            ))

    def clear_search(self):
        #Borra la exploración anterior y regresa el ratón al inicio
        if self.after_id is not None:  # si hay una acción programada pendiente...
            self.master.after_cancel(self.after_id)  # ...la cancelamos
            self.after_id = None       # ya no hay nada pendiente
        self.animating = False         # ninguna animación en curso
        self.btn_bfs.config(state="normal")  # aseguramos que el botón esté activo

        self.canvas.delete("explorado")  # borra las celdas azules
        self.canvas.delete("camino")   # borra el rastro dorado
        self.player_position = list(start)  # el ratón vuelve a la posición inicial
        self.draw_player()             # lo redibuja ahí

    def new_maze(self):
        #Genera otro laberinto del mismo tamaño
        self.clear_search()            # limpia animación y regresa el ratón

        self.grid = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]  # rellena todo con paredes
        self.create_maze()             # vuelve a tallar un laberinto nuevo
        self.canvas.delete("all")      # borra todo el dibujo anterior
        self.draw_maze()               # dibuja el nuevo laberinto
        self.draw_player()             # dibuja al ratón en el inicio
        self.status.config(text="Presiona 'Resolver con BFS'")  # restablece el mensaje


def start_game(level):
    global root                        # usaremos la variable global root
    root.destroy()                     # cierra la ventana del menú
    root = tk.Tk()                     # crea la ventana del juego
    root.title("Maze Game - BFS")      # título de la ventana

    if level == "Fácil":               # nivel fácil
        MazeSolverBFS(root, easy_grid_size)  # laberinto pequeño
    elif level == "Medio":             # nivel medio
        MazeSolverBFS(root, medium_grid_size)  # laberinto mediano
    elif level == "Difícil":           # nivel difícil
        MazeSolverBFS(root, hard_grid_size)  # laberinto grande


if __name__ == "__main__":             # solo corre al ejecutar este archivo directamente
    root = tk.Tk()                     # ventana del menú
    root.title("Maze Game - BFS")      # título de la ventana

    tk.Label(root, text="Selecciona la dificultad del nivel: ", font=("Times New Roman", 14)).pack(pady=10)  # texto del menú
    tk.Button(root, text="Fácil", command=lambda: start_game("Fácil")).pack(pady=5)  # botón nivel fácil
    tk.Button(root, text="Medio", command=lambda: start_game("Medio")).pack(pady=5)  # botón nivel medio
    tk.Button(root, text="Difícil", command=lambda: start_game("Difícil")).pack(pady=5)  # botón nivel difícil

    root.mainloop()                    # inicia el ciclo de eventos de la ventana
