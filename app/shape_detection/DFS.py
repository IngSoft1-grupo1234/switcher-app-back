from algoritmo import ShapeFitChecker
from shapes import SHAPE_TYPES
import random

class ShapeDetector:
    def __init__(self):
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(self, board, visited, row, col, color):
        stack = [(row, col)]
        group = []

        while stack:
            r, c = stack.pop()
            if not visited[r][c]:
                visited[r][c] = True
                group.append((r, c))
        
                # Chequea vecinos
                for dr, dc in self.directions:
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < len(board) and 0 <= new_c < len(board[0]):
                        if not visited[new_r][new_c] and board[new_r][new_c] == color:
                            stack.append((new_r, new_c))
        
        return group

    def find_color_groups(self, board):
        rows = len(board)
        cols = len(board[0])
        visited = [[False] * cols for _ in range(rows)]
        color_groups = []

        for row in range(rows):
            for col in range(cols):
                if not visited[row][col]:
                    color = board[row][col]
                    group = self.dfs(board, visited, row, col, color)
                    if group:
                        color_groups.append((color, group))

        return color_groups

    def test_shape_fitting(self, board):
        color_groups = self.find_color_groups(board)
        color_name = { 'r': 'Red', 'g': 'Green', 'b': 'Blue', 'y': 'Yellow' }

        sf = ShapeFitChecker()
        formas_disponibles = sf.formas_disponibles

        iteration_count = 0
        shape_count = 0

        for i, (color, group) in enumerate(color_groups):
            if len(group) < 3:
                continue
            sorted_group = sorted(group, key=lambda x: x[1])
            row, col = sorted_group[0]
            for keys in formas_disponibles[col][row]:
                for shapes in SHAPE_TYPES[keys]:
                    iteration_count += 1
                    var = SHAPE_TYPES[keys][shapes](row, col)
                    if len(var) == len(group) and sorted(group) == sorted(var):
                        shape_count += 1
                        print(f"THERE IS A {color_name[color]} {shapes} IN THE BOARD")
                        break  # Si encuentra figura rompe el loop
                else:
                    continue  # continua el loop grande si no se rompe el loop chiquito
                break  # si se rompe el chiquito entra aca y rompe el grande
        # print(f"Total number of iterations: {iteration_count}")
        # print(f"Total number of shapes found: {shape_count}")
        return iteration_count

if __name__ == "__main__":
    dfs = ShapeDetector()

    tablero = [
        ['r', 'g', 'b', 'y', 'r', 'r'],
        ['r', 'r', 'y', 'r', 'r', 'g'],
        ['r', 'y', 'r', 'g', 'g', 'g'],
        ['y', 'b', 'g', 'b', 'y', 'g'],
        ['r', 'b', 'b', 'r', 'y', 'r'],
        ['g', 'r', 'b', 'y', 'y', 'b']
    ]

    dfs.test_shape_fitting(tablero)

    """ def generate_random_board(rows, cols, colors):
        return [[random.choice(colors) for _ in range(cols)] for _ in range(rows)]

    # Generate a random board
    rows, cols = 6, 6
    colors = ['r', 'g', 'b', 'y']
    tablero = generate_random_board(rows, cols, colors)
    dfs.test_shape_fitting(tablero) # aqui tablero

    total_iterations = 0
    num_tests = 1000

    for _ in range(num_tests):
        tablero = generate_random_board(rows, cols, colors)
        total_iterations += dfs.test_shape_fitting(tablero)

    average_iterations = total_iterations / num_tests
    print(f"Average number of iterations over {num_tests} tests: {average_iterations}") """