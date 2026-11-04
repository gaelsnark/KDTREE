class Node:
    """A node in the 2D kd-tree."""

    def __init__(self, point=None, line_coord=None, axis=None, left=None, right=None):
        self.point = point          
        self.line_coord = line_coord  
        self.axis = axis            
        self.left = left            
        self.right = right          

    def is_leaf(self):
        return self.point is not None


def build_kd_tree(points, depth=0):
    if not points:
        return None
    
    if len(points) == 1:
        return Node(point=points[0])

    # NOTA: Alterna el eje de división en cada nivel (0 para X, 1 para Y).
    axis = depth % 2

    # NOTA: Ordena los puntos basándose exclusivamente en el eje activo actual.
    points_sorted = sorted(points, key=lambda p: p[axis])
    
    median_idx = (len(points_sorted) - 1) // 2
    median_coord = points_sorted[median_idx][axis]
    
    p1 = points_sorted[: median_idx + 1]
    p2 = points_sorted[median_idx + 1 :]
    
    left_child = build_kd_tree(p1, depth + 1)
    right_child = build_kd_tree(p2, depth + 1)
    
    # NOTA: Retorna un nodo interno que almacena la línea de corte (line_coord) y el eje.
    return Node(
        line_coord=median_coord,
        axis=axis,
        left=left_child,
        right=right_child
    )


def search_kd_tree(node, R):
    if node is None:
        return []

    # NOTA: Si es hoja, evalúa mediante condiciones si el punto está dentro del rectángulo R.
    if node.is_leaf():
        x, y = node.point
        (xmin, xmax), (ymin, ymax) = R
        if xmin <= x <= xmax and ymin <= y <= ymax:
            return [node.point]
        return []

    points_found = []
    axis = node.axis
    r_min, r_max = R[axis]

    # NOTA: Poda (pruning) de la rama izquierda si el rango de búsqueda no la cruza.
    if node.left and r_min <= node.line_coord:
        points_found.extend(search_kd_tree(node.left, R))

    # NOTA: Poda (pruning) de la rama derecha si el rango de búsqueda no la cruza.
    if node.right and r_max >= node.line_coord:
        points_found.extend(search_kd_tree(node.right, R))

    return points_found


# --- 1. Datos y prueba del árbol KD ---
puntos = [(2, 3), (5, 4), (9, 6), (4, 7), (8, 1), (7, 2)]
raiz = build_kd_tree(puntos, depth=0)
rango_R = ((4, 8), (1, 5))
puntos_encontrados = search_kd_tree(raiz, rango_R)

print(f"Puntos de entrada: {puntos}")
print(f"Rango de consulta R: X en [4, 8], Y en [1, 5]")
print(f"Puntos dentro del rango: {puntos_encontrados}")


class Mouse:
    def __init__(self, start_pos, target_pos, kd_tree_root):
        self.current_pos = start_pos
        self.target_pos = target_pos
        self.kd_tree = kd_tree_root
        self.visited = {start_pos}
        self.path = [start_pos]

    def get_adjacent_valid_steps(self):
        """Usa SEARCHKDTREE para obtener celdas caminables a distancia 1 del ratón."""
        x, y = self.current_pos
        
        # NOTA: Define una caja delimitadora cuadrada de radio 1 alrededor de la posición actual.
        search_range = ((x - 1, x + 1), (y - 1, y + 1))
        
        # Obtiene los candidatos cercanos utilizando la velocidad del árbol KD
        candidates = search_kd_tree(self.kd_tree, search_range)
        
        valid_neighbors = []
        for cx, cy in candidates:
            # NOTA: Calcula la distancia de Manhattan para verificar cercanía.
            dist_manhattan = abs(cx - x) + abs(cy - y)
            
            # NOTA: Filtra para asegurar movimiento ortogonal estricto (distancia 1) y casilla no visitada.
            if dist_manhattan == 1 and (cx, cy) not in self.visited:
                valid_neighbors.append((cx, cy))
                
        return valid_neighbors