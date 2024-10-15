from .shapes import SHAPE_TYPES

class ShapeFitChecker:
    def __init__(self):
        self.formas_disponibles = [[[] for _ in range(6)] for _ in range(6)]
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

                #print("Tuplas disponibles para la fila ", fila, " y columna ", columna, " son: ", tuplas_filtradas)


    

