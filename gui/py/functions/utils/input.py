from ..models.matriz import Matriz
from .latparser import eval_latex, Operand

import sympy


def fraction_make(input: str) -> sympy.Expr:
    res: Operand = eval_latex(input, None)
    if not isinstance(res, sympy.Expr):
        raise Exception("Entrada invalida")
    return res


def matrix_make(input: list[list[str]]) -> Matriz:
    if len(input) == 0:
        raise Exception("No se ingresaron datos")

    agreed_column_count = len(input[0])
    mat: Matriz = Matriz(len(input), agreed_column_count)
    for i, f in enumerate(input):
        if len(f) != agreed_column_count:
            raise Exception("Matrix is not consistent in its size")
        for j, c in enumerate(f):
            frac = fraction_make(c)
            mat.set(i + 1, j + 1, frac)

    return mat
