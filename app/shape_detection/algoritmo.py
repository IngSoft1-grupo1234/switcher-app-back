from shapes import SHAPE_TYPES

class ShapeFitChecker:
    def __init__(self):
        self.formas_disponibles = [[[] for _ in range(6)] for _ in range(6)]
        self.tamanio_formas_disponibles = {}
        self._populate_formas_disponibles()

    def _populate_formas_disponibles(self):
        for columna in range(6):
            for fila in range(6):
                boundfila = 5 - fila
                boundcolumna = 5 - columna
                boundnegfila = fila
                tuplas_filtradas = [shape_type for shape_type in SHAPE_TYPES 
                                    if shape_type[0] <= boundfila and shape_type[1] <= boundcolumna and shape_type[2] <= boundnegfila]
                self.formas_disponibles[columna][fila] = tuplas_filtradas

                for tupla in tuplas_filtradas:
                    for shapes in SHAPE_TYPES[tupla]:
                        if tupla not in self.tamanio_formas_disponibles:
                            self.tamanio_formas_disponibles[tupla] = {}
                        self.tamanio_formas_disponibles[tupla][shapes] = len(SHAPE_TYPES[tupla][shapes](0,0))

                #print("Tuplas disponibles para la fila ", fila, " y columna ", columna, " son: ", tuplas_filtradas)

    def _populate_tamanio_formas_disponibles(self):
        for columna in range(6):
            for fila in range(6):
                for shape_type in self.formas_disponibles[columna][fila]:
                    if shape_type not in self.tamanio_formas_disponibles:
                        self.tamanio_formas_disponibles[shape_type] = 1
                    else:
                        self.tamanio_formas_disponibles[shape_type] += 1
if __name__ == "__main__":
    shape_detector = ShapeFitChecker()
    formas_disponibles = shape_detector.formas_disponibles
    tamanio_formas_disponibles = shape_detector.tamanio_formas_disponibles
    print((SHAPE_TYPES[(2, 2, 0)]["SHAPE_1_A"](0,0))) 
    print(f"{tamanio_formas_disponibles[(2, 2, 0)]["SHAPE_1_A"]}")

    

