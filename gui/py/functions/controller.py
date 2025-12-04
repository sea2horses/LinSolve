from .utils import latex as latex
from .utils import input as input
from .utils import latparser as parser
from .utils.auxiliar import sympy_expr
import sympy

from .models import matriz, vector

from .operations import funciones as fn
from .operations import operaciones as op

import json
import re
from typing import Any, Dict, Union


def resolver_sistema_por_gauss_jordan(mat: list[list[str]], ecuaciones: int, incognitas: int) -> str:
    accmat = input.matrix_make(mat)
    latex.LATEX_STDOUT.clear()
    fn.resolver_sistema(accmat, ecuaciones, incognitas)
    return latex.LATEX_STDOUT.stdout


def json_a_operando(_json: str) -> Union[parser.Operand, Dict[str, parser.Operand | None]]:
    # Try to load JSON normally, but tolerate single quotes and unquoted keys
    try:
        data = json.loads(_json)
    except Exception:
        # Replace single quotes with double quotes
        s = _json.replace("'", '"')

        # Quote unquoted keys: { key: -> { "key":
        s = re.sub(r'([\{,\s])(\w+)\s*:', r'\1"\2":', s)

        data = json.loads(s)

    # If top-level is a mapping of variable names to descriptors, convert to env dict
    if isinstance(data, dict) and not ("type" in data and "contents" in data):
        env: dict[str, parser.Operand | None] = {}
        for name, desc in data.items():
            # desc should be an object with type/contents
            if not isinstance(desc, dict):
                raise ValueError(f"Invalid descriptor for variable {name}")
            operand = json_a_operando(json.dumps(desc))
            if isinstance(operand, dict):
                raise ValueError(
                    f"Nested variable directory not allowed for variable {name}")
            env[name] = operand
        return env

    # Otherwise expect a single operand descriptor
    type_ = data.get("type")
    contents: Any = data.get("contents")

    if type_ == "Matrix":
        # contents expected to be a list of rows (each row a list of strings)
        if not isinstance(contents, list) or not contents:
            raise ValueError(
                "Matrix contents must be a non-empty list of rows")

        rows = len(contents)
        cols = len(contents[0])
        mat = matriz.Matriz(rows, cols)

        for i, row in enumerate(contents):
            if not isinstance(row, list) or len(row) != cols:
                raise ValueError(
                    "All matrix rows must have the same number of columns")
            for j, cell in enumerate(row):
                # cell expected to be a LaTeX-like string; use parser.eval_latex to get sympy.Expr
                if isinstance(cell, (int, float)):
                    val = cell
                else:
                    val = parser.eval_latex(str(cell), None)

                # Ensure scalar
                if hasattr(val, "matriz") or hasattr(val, "componentes"):
                    raise ValueError("Matrix cell evaluated to non-scalar")

                mat.set(i + 1, j + 1, val)

        return mat

    if type_ == "Vector":
        # contents expected to be a list of scalars
        if not isinstance(contents, list) or not contents:
            raise ValueError("Vector contents must be a non-empty list")

        comps: list[Any] = []
        for cell in contents:
            if isinstance(cell, (int, float)):
                val = cell
            else:
                val = parser.eval_latex(str(cell), None)

            if hasattr(val, "matriz") or hasattr(val, "componentes"):
                raise ValueError("Vector component evaluated to non-scalar")

            comps.append(val)

        return vector.Vector(comps)

    if type_ == "Expression":
        # contents may be a single string expression
        if isinstance(contents, list):
            # join if list provided
            expr_str = " ".join(map(str, contents))
        else:
            expr_str = str(contents)

        return parser.eval_latex(expr_str, None)

    raise ValueError(f"Unknown operand type: {type_}")


def evaluar_latex(m: str, varjson: str | None = None) -> str:
    env = parser.reserved_env.copy()
    if varjson is not None:
        parsed = json_a_operando(varjson)
        if isinstance(parsed, dict):
            env.update(parsed)

    result: parser.Operand = parser.eval_latex(m, env)

    if isinstance(result, matriz.Matriz):
        return latex.matrix(result)
    elif isinstance(result, vector.Vector):
        return latex.vector(result)
    else:
        return latex.number_parse(result)


def comparar_expresiones(expr1: str, expr2: str, varjson: str | None = None) -> str:
    """
    Devuelve LaTeX indicando si expr1 == expr2 bajo el mismo ambiente.
    """
    env = parser.reserved_env.copy()
    if varjson is not None:
        parsed = json_a_operando(varjson)
        if isinstance(parsed, dict):
            env.update(parsed)

    a = parser.eval_latex(expr1, env)
    b = parser.eval_latex(expr2, env)

    def mat_eq(m1: matriz.Matriz, m2: matriz.Matriz) -> bool:
        if m1.filas != m2.filas or m1.columnas != m2.columnas:
            return False
        for i in range(1, m1.filas + 1):
            for j in range(1, m1.columnas + 1):
                if sympy.simplify(m1.at(i, j) - m2.at(i, j)) != 0:
                    return False
        return True

    def vec_eq(v1: vector.Vector, v2: vector.Vector) -> bool:
        if v1.dimension != v2.dimension:
            return False
        for i in range(1, v1.dimension + 1):
            if sympy.simplify(v1.at(i) - v2.at(i)) != 0:
                return False
        return True

    def latex_repr(val: parser.Operand) -> str:
        if isinstance(val, matriz.Matriz):
            return latex.matrix(val)
        if isinstance(val, vector.Vector):
            return latex.vector(val)
        if isinstance(val, sympy.Expr):
            return latex.sympy_expression(val)
        return latex.text(str(val))

    if isinstance(a, sympy.Expr) and isinstance(b, sympy.Expr):
        iguales = sympy.simplify(a - b) == 0
    elif isinstance(a, matriz.Matriz) and isinstance(b, matriz.Matriz):
        iguales = mat_eq(a, b)
    elif isinstance(a, vector.Vector) and isinstance(b, vector.Vector):
        iguales = vec_eq(a, b)
    else:
        iguales = False
    latex.LATEX_STDOUT.clear()
    latex.LATEX_STDOUT.writelatex(latex.text("Expr 1:") + latex.newline() + latex_repr(a) + latex.newline())
    latex.LATEX_STDOUT.writelatex(latex.text("Expr 2:") + latex.newline() + latex_repr(b) + latex.newline())
    latex.LATEX_STDOUT.writelatex(latex.text(f"Comparando: {expr1} =? {expr2}") + latex.newline())
    latex.LATEX_STDOUT.writelatex(latex.text(f"Resultado: {'iguales' if iguales else 'diferentes'}") + latex.newline())
    return latex.LATEX_STDOUT.stdout


# ---------- Wrappers expuestos a Eel para matrices y vectores ----------


def _vector_make(vals: list[str]) -> vector.Vector:
    comps = [parser.eval_latex(str(v), None) if not isinstance(v, (int, float))
             else v for v in vals]
    return vector.Vector(comps)


def sumar_matrices(m1: list[list[str]], m2: list[list[str]]) -> str:
    latex.LATEX_STDOUT.clear()
    a = input.matrix_make(m1)
    b = input.matrix_make(m2)
    res = op.suma_matrices(a, b)
    latex.LATEX_STDOUT.writelatex(latex.matrix(res))
    return latex.LATEX_STDOUT.stdout


def restar_matrices(m1: list[list[str]], m2: list[list[str]]) -> str:
    latex.LATEX_STDOUT.clear()
    a = input.matrix_make(m1)
    b = input.matrix_make(m2)
    res = op.resta_matrices(a, b)
    latex.LATEX_STDOUT.writelatex(latex.matrix(res))
    return latex.LATEX_STDOUT.stdout


def multiplicar_matrices(m1: list[list[str]], m2: list[list[str]]) -> str:
    latex.LATEX_STDOUT.clear()
    a = input.matrix_make(m1)
    b = input.matrix_make(m2)
    res = op.multiplicar_matrices(a, b)
    latex.LATEX_STDOUT.writelatex(latex.matrix(res))
    return latex.LATEX_STDOUT.stdout


def determinante_cofactores(m1: list[list[str]]) -> str:
    latex.LATEX_STDOUT.clear()
    a = input.matrix_make(m1)
    det = op.determinante_por_cofactores(a)
    latex.LATEX_STDOUT.writelatex(latex.number_parse(det))
    return latex.LATEX_STDOUT.stdout


def determinante_sarrus(m1: list[list[str]]) -> str:
    latex.LATEX_STDOUT.clear()
    a = input.matrix_make(m1)
    det = op.determinante_por_sarrus(a)
    latex.LATEX_STDOUT.writelatex(latex.number_parse(det))
    return latex.LATEX_STDOUT.stdout


def sumar_vectores(v1: list[str], v2: list[str]) -> str:
    latex.LATEX_STDOUT.clear()
    a = _vector_make(v1)
    b = _vector_make(v2)
    res = op.suma_vectores(a, b)
    latex.LATEX_STDOUT.writelatex(latex.vector(res))
    return latex.LATEX_STDOUT.stdout


def restar_vectores(v1: list[str], v2: list[str]) -> str:
    latex.LATEX_STDOUT.clear()
    a = _vector_make(v1)
    b = _vector_make(v2)
    res = op.resta_vectores(a, b)
    latex.LATEX_STDOUT.writelatex(latex.vector(res))
    return latex.LATEX_STDOUT.stdout


def escalar_vector(v: list[str], escalar: str) -> str:
    latex.LATEX_STDOUT.clear()
    vec = _vector_make(v)
    res = op.vector_por_escalar(vec, parser.eval_latex(escalar, None))
    latex.LATEX_STDOUT.writelatex(latex.vector(res))
    return latex.LATEX_STDOUT.stdout


def matriz_por_vector(m1: list[list[str]], v: list[str]) -> str:
    latex.LATEX_STDOUT.clear()
    mat = input.matrix_make(m1)
    vec = _vector_make(v)
    res = op.matriz_por_vector(mat, vec)
    latex.LATEX_STDOUT.writelatex(latex.vector(res))
    return latex.LATEX_STDOUT.stdout


def combinacion_lineal_vectores(vectors: list[list[str]], target: list[str]) -> str:
    latex.LATEX_STDOUT.clear()
    vecs = [_vector_make(v) for v in vectors]
    tgt = _vector_make(target)
    fn.combinacion_lineal(tgt.dimension, vecs, tgt)
    return latex.LATEX_STDOUT.stdout


def dependencia_lineal_vectores(vectors: list[list[str]]) -> str:
    latex.LATEX_STDOUT.clear()
    vecs = [_vector_make(v) for v in vectors]
    fn.dependencia_lineal(vecs[0].dimension, vecs)
    return latex.LATEX_STDOUT.stdout


def resolver_cramer(coeffs: list[list[str]], results: list[str]) -> str:
    """
    Resuelve un sistema Ax = b usando regla de Cramer.
    """
    latex.LATEX_STDOUT.clear()
    A = input.matrix_make(coeffs)
    b_vec = _vector_make(results)

    if A.filas != A.columnas:
        raise ValueError("La matriz de coeficientes debe ser cuadrada.")
    if b_vec.dimension != A.filas:
        raise ValueError("El vector de resultados debe tener la misma cantidad de filas que A.")

    n = A.filas
    detA = op.determinante_por_cofactores(A)
    latex.LATEX_STDOUT.writelatex(latex.text("Determinante de A: ") + latex.number_parse(detA) + latex.newline())

    if detA == 0:
        latex.LATEX_STDOUT.writelatex(latex.text("El sistema no tiene solución única (det(A)=0).") + latex.newline())
        return latex.LATEX_STDOUT.stdout

    soluciones = []
    for col in range(1, n + 1):
        Ai = matriz.Matriz(A.filas, A.columnas)
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                Ai.set(i, j, b_vec.at(i) if j == col else A.at(i, j))
        detAi = op.determinante_por_cofactores(Ai)
        xi = detAi / detA
        soluciones.append(xi)
        latex.LATEX_STDOUT.writelatex(
            latex.text(f"det(A{col}) = ") + latex.number_parse(detAi) + latex.text(f", x_{col} = det(A{col})/det(A)") + latex.newline()
        )

    latex.LATEX_STDOUT.writelatex(latex.text("Solución por Cramer:") + latex.newline())
    for idx, val in enumerate(soluciones, start=1):
        latex.LATEX_STDOUT.writelatex(latex.text(f"x_{idx} = ") + latex.number_parse(val) + latex.newline())
    return latex.LATEX_STDOUT.stdout
