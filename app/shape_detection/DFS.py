from .algoritmo import ShapeFitChecker
from .shapes import SHAPE_TYPES


class ShapeDetector:
    def __init__(self):
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        sf = ShapeFitChecker()
        if not hasattr(self.__class__, 'formas_disponibles'): # velocida' 
            self.__class__.formas_disponibles = sf.formas_disponibles

    def dfs(self, board, visited, row, col, color):
        stack = [(row, col)]
        group = []

        while stack:
            r, c = stack.pop()
            if not visited[r][c]:
                visited[r][c] = True
                group.append((r, c))
        
                # Chequea vecinos
                # se podria crear una lista con los movimientos posibles por casilla
                # y reducir iteraciones :nerd: :mano_para_arriba:
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
        print(f"Color groups: {color_groups}")
        color_name = { 'r': 'Red', 'g': 'Green', 'b': 'Blue', 'y': 'Yellow' }

        sf = ShapeFitChecker()
        formas_disponibles = self.formas_disponibles

        result = {}
 
        key = 1

        for i, (color, group) in enumerate(color_groups):
            if len(group) < 3 or len(group) > 5:
                continue
            sorted_group = sorted(group, key=lambda x: x[1])
            # print(f"sorted  group: {sorted_group}, color: {color_name[color]}")
            row, col = sorted_group[0]
            for keys in formas_disponibles[col][row]:
                for shapes in SHAPE_TYPES[keys]:
                    var = SHAPE_TYPES[keys][shapes](row, col)
                    if len(var) == len(group) and sorted(group) == sorted(var):
                        shape_number = int(shapes.split('_')[1])
                        result[key] = {
                            'color': color,
                            'shape': shape_number,
                            'positions': var
                        }
                        key += 1
                        #print(f"THERE IS A {color_name[color]} {shapes} IN THE BOARD")
                        break  
                else:
                    continue  
                break  
        return result
    
    def pretty_print_result(self, shapes):
        print("\n\n" + "="*30 + "  SHAPES DETECTED  " + "="*31)
        for shape in shapes:
            print(f"Color: {shapes[shape]['color']}")
            print(f"Shape Type: {shapes[shape]['shape']}")
            print(f"Coordinates: {shapes[shape]['positions']}")
            print("-"*70)
        print("="*80 + "\n\n")