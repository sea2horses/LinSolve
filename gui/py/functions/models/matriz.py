from fractions import Fraction
from ..utils.auxiliar import sympy_expr
from typing import Any

import sympy


class Matriz:
    # Representa a la matriz,
    matriz: list[list[sympy.Expr]] = []
    filas = 0
    columnas = 0
    linea = -1

    # Constructor de la clase
    def __init__(self, filas: int, columnas: int, linea: int = -1):
        if filas <= 0 or columnas <= 0:
            # Tiramos un error si alguno de los dos numeros es invalido
            raise Exception(
                "El numero de filas y columnas tienen que ser mayores a 0")

        # Rellenamos las filas y columnas
        self.filas = filas
        self.columnas = columnas
        self.matriz = []

        for i in range(0, filas):
            # Inicializamos cada una de las filas
            self.matriz.append([])
            for _ in range(0, columnas):
                # Inicializamos todo a 0
                self.matriz[i].append(sympy_expr(0))

    # Check de limites
    # Lo puse entre dos barras bajas porque es un metodo 'privado' (no lo va a usar el usuario de la clase)
    def _boundcheck_(self, fila: int, columna: int) -> None:
        if fila > self.filas or columna > self.columnas or fila <= 0 or columna <= 0:
            raise Exception(
                f"Sobrepaso de indice, se pidió la posición ({fila},{columna}) en una matriz de {self.filas}x{self.columnas}")

    # Indice
    def at(self, fila: int, columna: int) -> sympy.Expr:
        self._boundcheck_(fila, columna)
        # como los arreglos en python empiezan a contar de 0, restemos 1
        # asi la posicion #1 se convierte a 0, la verdadera posicion inicial
        return self.matriz[fila-1][columna-1]

    def row(self, fila: int) -> list[sympy.Expr]:
        return self.matriz[fila - 1]

    def column(self, columna: int) -> list[sympy.Expr]:
        column: list[sympy.Expr] = []
        for row in self.matriz:
            column.append(row[columna - 1])

        return column

    # Set
    def set(self, fila: int, columna: int, valor: Any) -> None:
        self._boundcheck_(fila, columna)
        # Explicacion en la funcion d arriba
        self.matriz[fila - 1][columna - 1] = sympy_expr(valor)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Matriz):
            return False

        if other.filas != self.filas or other.columnas != self.columnas:
            return False

        for i in range(1, self.filas + 1):
            for j in range(1, self.columnas + 1):
                if self.at(i, j) != other.at(i, j):
                    return False

        return True

        # Este metodo copia la matriz
    def copy(self) -> "Matriz":
        copia: Matriz = Matriz(self.filas, self.columnas)

        for i in range(1, self.filas + 1):
            for j in range(1, self.columnas + 1):
                copia.set(i, j, self.at(i, j))

        return copia
