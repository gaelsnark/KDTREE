class Node:
    """A node in the 2D kd-tree."""

    def __init__(self, point=None, line_coord=None, axis=None, left=None, right=None):
        self.point = point          # Stored point (for leaf nodes)
        self.line_coord = line_coord  # Median x or y coordinate (for internal nodes)
        self.axis = axis            # Splitting axis: 0 for vertical (x), 1 for horizontal (y)
        self.left = left            # Left/Below child
        self.right = right          # Right/Above child

    def is_leaf(self):
        return self.point is not None


def build_kd_tree(points, depth=0):
    """
    Builds a 2D kd-tree recursively from a list of 2D points (tuples/lists of (x, y)).
    
    :param points: List of points, e.g., [(x1, y1), (x2, y2), ...]
    :param depth: Current depth of the tree (0-indexed)
    :return: Root Node of the kd-tree
    """
    if not points:
        return None

    # Base case: 1 point left -> Leaf node
    if len(points) == 1:
        return Node(point=points[0])

    # Determine axis: Even depth -> x-axis (0), Odd depth -> y-axis (1)
    axis = depth % 2

    # Sort points along the splitting axis to find the median
    points_sorted = sorted(points, key=lambda p: p[axis])
    
    # Median index (lower median for even-length lists to follow convention)
    median_idx = (len(points_sorted) - 1) // 2
    median_coord = points_sorted[median_idx][axis]

    # Split into P1 (left/below or on line) and P2 (right/above line)
    p1 = points_sorted[: median_idx + 1]
    p2 = points_sorted[median_idx + 1 :]

    # Recursively build subtrees
    left_child = build_kd_tree(p1, depth + 1)
    right_child = build_kd_tree(p2, depth + 1)

    # Return internal node storing the splitting line
    return Node(
        line_coord=median_coord,
        axis=axis,
        left=left_child,
        right=right_child
    )