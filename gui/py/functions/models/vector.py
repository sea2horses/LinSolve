from fractions import Fraction
from ..utils.auxiliar import sympy_expr
from ..models.number import Number
import sympy
from typing import Any
from enum import Enum


class VectorTipo(Enum):
    FILA = 0
    COLUMNA = 1


class Vector:
    componentes: list[sympy.Expr]
    dimension: int
    tipo: VectorTipo = VectorTipo.COLUMNA

    def __init__(self, componentes: Any):
        if not componentes:
            raise Exception("Un vector no puede estar vacío.")

        self.componentes = list(
            sympy_expr(comp) for comp in componentes)
        self.dimension = len(componentes)

    def at(self, indice: int) -> sympy.Expr:
        """
        Devuelve el valor en la posición `indice` (1-indexado).
        """
        if indice <= 0 or indice > self.dimension:
            raise Exception(
                f"Índice fuera de rango: se pidió el componente {indice} de un vector de dimensión {self.dimension}")
        return self.componentes[indice - 1]

    def set(self, indice: int, valor: Number) -> None:
        """
        Establece el valor en la posición `indice` (1-indexado).
        """
        if indice <= 0 or indice > self.dimension:
            raise Exception(
                f"Índice fuera de rango: se intentó modificar el componente {indice} en un vector de dimensión {self.dimension}")
        self.componentes[indice - 1] = sympy_expr(valor)

    def transpose(self) -> None:
        if self.tipo == VectorTipo.COLUMNA:
            self.tipo = VectorTipo.FILA
        else:
            self.tipo = VectorTipo.COLUMNA

    def __str__(self) -> str:
        """
        Devuelve una representación legible del vector.
        Ejemplo: [1, 2.5, -3.75]
        """
        return "(" + ", ".join(str(x) for x in self.componentes) + ")"

    def __len__(self) -> int:
        """
        Permite usar len(vector) para obtener su dimensión.
        """
        return self.dimension

    def copy(self) -> "Vector":
        """
        Devuelve una copia del vector.
        """
        return Vector(self.componentes.copy())
