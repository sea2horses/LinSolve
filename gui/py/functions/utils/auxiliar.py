from fractions import Fraction
from typing import TypeVar
from ..models.number import Number
import sympy
import sympy.parsing.sympy_parser

T = TypeVar("T")


def array_top(arr: list[T]) -> T:
    return arr[len(arr) - 1]


def sympy_expr(x: str | Number) -> sympy.Expr:
    """
    Convierte a sympy.Expr aceptando enteros, fracciones, decimales y LaTeX simple.
    """
    try:
        if isinstance(x, sympy.Expr):
            return x
        elif isinstance(x, Fraction):
            return sympy.Rational(x.numerator, x.denominator)
        elif isinstance(x, str):
            try:
                return sympy_expr(decimal_a_fraccion(x))
            except Exception:
                # ultimo recurso: parser de sympy
                return sympy.parsing.sympy_parser.parse_expr(x)
        elif isinstance(x, int):
            return sympy.Integer(x)
        else:
            return sympy_expr(decimal_a_fraccion(str(x)))
    except Exception as e:
        raise ValueError(f"Entrada invalida: {x}") from e


def decimal_a_fraccion(x: str) -> Fraction:
    """
    Convierte strings numericos (enteros o decimales) a Fraction exacta.
    Soporta valores como "0.5", ".5", "1.", "-0.0".
    """
    s = x.strip()
    if s == "":
        return Fraction(0)

    if s.startswith("."):
        s = "0" + s
    if s.endswith("."):
        s = s[:-1]

    try:
        return Fraction(s)
    except Exception:
        try:
            return Fraction(float(s)).limit_denominator()
        except Exception as e:
            raise ValueError("Entrada invalida") from e
