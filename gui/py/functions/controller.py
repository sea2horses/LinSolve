from .utils import latex as latex
from .utils import input as input
from .utils import latparser as parser

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
    env = None
    if varjson is not None:
        parsed = json_a_operando(varjson)
        # If parsed is a dict, use it as environment; otherwise ignore
        if isinstance(parsed, dict):
            # Merge with reserved env (copy to avoid mutation)
            env = parser.reserved_env.copy()
            env.update(parsed)
        else:
            # single operand not directly usable as env; ignore
            env = parser.reserved_env.copy()

    result: parser.Operand = parser.eval_latex(m, env)

    if isinstance(result, matriz.Matriz):
        return latex.matrix(result)
    elif isinstance(result, vector.Vector):
        return latex.vector(result)
    else:
        return latex.number_parse(result)
