
import tkinter as tk
import random
import time 

#Variables que usaremos
#Cada celda mide 40 * 40 píxeles
cell_size = 40
#Laberinto sencillo = 10x10 celdas
easy_grid_size = 10
#Laberijnto medio = 15x15 celdas
medium_grid_size = 15
#Laberinto díficil de 20x20
hard_grid_size = 20

#Posición inicial 
start = (0,0)

#root = variable donde guardaremos la ventana donde aparecera el laberinto
root = None

class MazeSolver:
    #master = ventana donde se mostrará el laberinto
    #canvas = es el espacio donde se dibujará el laberinto
    def __init__(self, master, grid_size):
        self.master = master 
        #establacer el tamaño inicial del laberinto 
        self.grid_size = grid_size

        #Canvas para dibujar el ratón
        self.canvas = tk.Canvas(master, width = grid_size * cell_size, height = grid_size * cell_size, bg="white")
        self.canvas.pack()

        #Empezamos la cuadricula poniendo paredes
        #self.grid = guarda la matriz del laberinto
        # 1 = pared
        self.grid = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        #Posición final del laberinto
        self.end = (grid_size - 1, grid_size - 1)

        self.create_maze()
        self.draw_maze()

        #posición inicial del ratón 
        self.player_position = list(start)

        #Dibujar el ratón
        self.draw_player()

    #Crear el ratón que resuelve el lberinto con método recursivo
    def create_maze(self):
        #Abrimos la primera celda
        self.grid[0][0] = 0

        self.recursive_backtrack(0,0)
        self.grid[start[0]][start[1]] = 0
        self.grid[self.end[0]][self.end[1]] = 0

        #Conectar la meta con los caminos del laberinto
        if self.grid_size % 2 == 0:
            self.grid[self.end[0] - 1][self.end[1]] = 0

    def recursive_backtrack(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2

            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.grid[nx][ny] == 1:
                self.grid[nx][ny] = 0
                self.grid[x + dx][y + dy] = 0
                self.recursive_backtrack(nx,ny)

    def draw_maze(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                color = "black" if self.grid[y][x] == 1 else "white"

                self.canvas.create_rectangle(
                    x * cell_size, y * cell_size,
                    (x + 1) * cell_size, (y + 1) * cell_size,
                    fill = color, outline = "gray"
                )

        #Dibujar el inicio y la meta
        self.canvas.create_rectangle(
            start[1] * cell_size, start[0] * cell_size,
            (start[1] + 1) * cell_size, (start[0] + 1) * cell_size,
            fill = "green"
        )

        self.canvas.create_rectangle(
            self.end[1] * cell_size, self.end[0] * cell_size,
            (self.end[1] + 1) * cell_size, (self.end[0] + 1) * cell_size,
            fill = "red"
        )

    def draw_player(self):
        self.canvas.delete("player")
        self.canvas.create_oval(
            self.player_position[1] * cell_size + 5,
            self.player_position[0] * cell_size + 5, 
            (self.player_position[1] + 1) * cell_size - 5, 
            (self.player_position[0] + 1) * cell_size -5, 
            fill="purple", tags = "player"
        )


def start_game(level):
    global root
    root.destroy()
    root = tk.Tk()
    root.title("Maze Game")

    if level == "Fácil":
        MazeSolver(root, easy_grid_size)
    elif level == "Medio":
        MazeSolver(root, medium_grid_size)
    elif level == "Difícil":
        MazeSolver(root, hard_grid_size)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Game")

    tk.Label(root, text="Selecciona la dificultad del nivel: ", font=("Times New Roman", 14)).pack(pady=10)
    tk.Button(root, text="Fácil", command=lambda: start_game("Fácil")).pack(pady=5)
    tk.Button(root, text="Medio", command=lambda: start_game("Medio")).pack(pady=5)
    tk.Button(root, text="Díficil", command=lambda: start_game("Difícil")).pack(pady=5)

    root.mainloop()
