# Interfaz con BFS para MiniMouse
# Reutiliza el laberinto y el ratón de interfaz.py SIN modificarlo:
# MazeSolverBFS hereda de MazeSolver y le agrega la búsqueda BFS.
#
# Ejecutar desde la raíz del repositorio:
#     python interfaz_bfs.py

import tkinter as tk
import time

from interfaz import (
    MazeSolver, cell_size, start,
    easy_grid_size, medium_grid_size, hard_grid_size,
)
from Minimouse.bfs import (
    SensorConContador,
    bfs,
    crear_sensor_fuerza_bruta,
    crear_sensor_kdtree,
    vecinos_desde_libres,
)

#Velocidad de la animación (milisegundos entre cada paso)
explore_delay = 25
walk_delay = 70

#root = ventana actual (igual que en interfaz.py)
root = None


class MazeSolverBFS(MazeSolver):
    # Nota: el BFS trabaja con (x, y) = (columna, fila), igual que el KD-Tree.
    # El grid y player_position usan [fila][columna], por eso se convierte.

    def __init__(self, master, grid_size):
        #Crea el laberinto, el canvas y el ratón con el código original
        super().__init__(master, grid_size)

        #Estado de la animación BFS
        self.animating = False
        self.after_id = None

        self.create_controls()

    def create_controls(self):
        #Panel con los botones y la selección del sensor
        panel = tk.Frame(self.master)
        panel.pack(pady=5)

        self.btn_bfs = tk.Button(panel, text="Resolver con BFS", command=self.solve_bfs)
        self.btn_bfs.grid(row=0, column=0, padx=5)

        self.btn_new = tk.Button(panel, text="Nuevo laberinto", command=self.new_maze)
        self.btn_new.grid(row=0, column=1, padx=5)

        #Sensor que usa el ratón para "ver" sus vecinos
        self.sensor_var = tk.StringVar(value="KD-Tree")
        tk.Radiobutton(panel, text="KD-Tree", variable=self.sensor_var,
                       value="KD-Tree").grid(row=0, column=2)
        tk.Radiobutton(panel, text="Fuerza bruta", variable=self.sensor_var,
                       value="Fuerza bruta").grid(row=0, column=3)

        self.status = tk.Label(self.master, text="Presiona 'Resolver con BFS'",
                               font=("Times New Roman", 11))
        self.status.pack(pady=(0, 8))

    def build_neighbors_function(self):
        #Puntos del KD-Tree = celdas libres del laberinto, como (x, y)
        free_cells = [
            (x, y)
            for y in range(self.grid_size)
            for x in range(self.grid_size)
            if self.grid[y][x] == 0
        ]

        sensor_name = self.sensor_var.get()
        if sensor_name == "KD-Tree":
            try:
                search = crear_sensor_kdtree(free_cells)
            except FileNotFoundError:
                #Si no está KD-Tree/Build&Search.py usamos fuerza bruta
                sensor_name = "Fuerza bruta"
                self.sensor_var.set(sensor_name)
                search = crear_sensor_fuerza_bruta(free_cells)
        else:
            search = crear_sensor_fuerza_bruta(free_cells)

        self.sensor = SensorConContador(search)
        self.sensor_name = sensor_name
        return vecinos_desde_libres(self.sensor)

    def solve_bfs(self):
        if self.animating:
            return

        self.clear_search()

        neighbors = self.build_neighbors_function()
        start_xy = (start[1], start[0])
        end_xy = (self.end[1], self.end[0])

        #Se calcula el BFS completo y después se anima paso a paso
        t0 = time.perf_counter()
        self.result = bfs(start_xy, end_xy, neighbors)
        self.elapsed_ms = (time.perf_counter() - t0) * 1000

        if not self.result.encontrado:
            self.status.config(text="No existe camino hasta la salida")
            return

        self.animating = True
        self.btn_bfs.config(state="disabled")
        self.status.config(text="Explorando con BFS...")
        self.animate_exploration(0)

    def paint_cell(self, x, y, color, tag):
        #No se pinta sobre el inicio ni la meta para conservar sus colores
        if (y, x) == start or (y, x) == self.end:
            return
        self.canvas.create_rectangle(
            x * cell_size, y * cell_size,
            (x + 1) * cell_size, (y + 1) * cell_size,
            fill=color, outline="gray", tags=tag
        )

    def animate_exploration(self, i):
        #Pinta de azul las celdas en el orden en que BFS las descubre
        explored = self.result.explorados

        if i < len(explored):
            x, y = explored[i]
            self.paint_cell(x, y, "lightblue", "explorado")
            self.canvas.tag_raise("player")
            self.after_id = self.master.after(explore_delay, self.animate_exploration, i + 1)
        else:
            self.status.config(text="Salida encontrada, el ratón sigue el camino más corto...")
            self.after_id = self.master.after(300, self.animate_walk, 0)

    def animate_walk(self, i):
        #El ratón recorre el camino más corto, dejando un rastro dorado
        path = self.result.camino

        if i < len(path):
            x, y = path[i]
            self.paint_cell(x, y, "gold", "camino")
            self.player_position = [y, x]
            self.draw_player()
            self.after_id = self.master.after(walk_delay, self.animate_walk, i + 1)
        else:
            self.animating = False
            self.btn_bfs.config(state="normal")
            self.status.config(text=(
                f"¡Salida encontrada! {self.result.pasos} pasos | "
                f"{len(self.result.explorados)} celdas exploradas | "
                f"{self.sensor.consultas} consultas ({self.sensor_name}) | "
                f"{self.elapsed_ms:.2f} ms"
            ))

    def clear_search(self):
        #Borra la exploración anterior y regresa el ratón al inicio
        if self.after_id is not None:
            self.master.after_cancel(self.after_id)
            self.after_id = None
        self.animating = False
        self.btn_bfs.config(state="normal")

        self.canvas.delete("explorado")
        self.canvas.delete("camino")
        self.player_position = list(start)
        self.draw_player()

    def new_maze(self):
        #Genera otro laberinto del mismo tamaño
        self.clear_search()

        self.grid = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.create_maze()
        self.canvas.delete("all")
        self.draw_maze()
        self.draw_player()
        self.status.config(text="Presiona 'Resolver con BFS'")


def start_game(level):
    global root
    root.destroy()
    root = tk.Tk()
    root.title("Maze Game - BFS")

    if level == "Fácil":
        MazeSolverBFS(root, easy_grid_size)
    elif level == "Medio":
        MazeSolverBFS(root, medium_grid_size)
    elif level == "Difícil":
        MazeSolverBFS(root, hard_grid_size)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Game - BFS")

    tk.Label(root, text="Selecciona la dificultad del nivel: ", font=("Times New Roman", 14)).pack(pady=10)
    tk.Button(root, text="Fácil", command=lambda: start_game("Fácil")).pack(pady=5)
    tk.Button(root, text="Medio", command=lambda: start_game("Medio")).pack(pady=5)
    tk.Button(root, text="Difícil", command=lambda: start_game("Difícil")).pack(pady=5)

    root.mainloop()
