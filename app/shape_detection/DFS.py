from algoritmo import ShapeFitChecker
from shapes import SHAPE_TYPES

class DFS:
    # Directions for moving in 4 directions (up, down, left, right)
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
        
                # Check the 4 neighbors
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
        # Find and print the groups
        color_groups = self.find_color_groups(board)
        color_name = { 'r': 'Red', 'g': 'Green', 'b': 'Blue', 'y': 'Yellow' }
        #for i, (color, group) in enumerate(color_groups):
            #print(f"Group {i+1}: Color {color_name[color]}, Size {len(group)}, Cells {group}")

        sf = ShapeFitChecker()
        formas_disponibles = sf.formas_disponibles

        iteration_count = 0

        for i, (color, group) in enumerate(color_groups):
            row, col = group[0]
            for keys in formas_disponibles[col][row]:
                for shapes in SHAPE_TYPES[keys]:
                    iteration_count += 1
                    var = SHAPE_TYPES[keys][shapes](row, col)
                    if len(var) == len(group) and sorted(group) == sorted(var):
                        print(f"THERE IS A {color_name[color]} {shapes} IN THE BOARD")
                        break  # Si encuentra figura rompe el loop
                else:
                    continue  # continua el loop grande si no se rompe el loop chiquito
                break  # si se rompe el chiquito entra aca y rompe el grande
        print(f"Total number of iterations: {iteration_count}")