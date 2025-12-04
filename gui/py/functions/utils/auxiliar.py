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
    Convierte un número (decimal o fracción en string) a Fraction exacta.
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
                return sympy.parsing.sympy_parser.parse_expr(x)
        elif isinstance(x, int):
            return sympy.Integer(x)
        else:
            return sympy_expr(decimal_a_fraccion(str(x)))
    except Exception as e:
        raise ValueError(f"Entrada inválida: {x}") from e


def decimal_a_fraccion(x: str) -> Fraction:
    trim: str = x.strip("0")
    if trim == "":
        return Fraction(0)

    if len(trim) > 12:
        raise ValueError("Number is too big")

    pieces: list[str] = trim.split(".")
    result_fraction: Fraction = Fraction(int(pieces[0]))
    if len(pieces) > 2 or trim.count('.') >= 2:
        raise ValueError("Excess of . in string")
    elif len(pieces) == 2:
        # Obtain decimal part
        f: Fraction = Fraction(0)
        # Get each decimal position
        for i, c in enumerate(pieces[1]):
            n: int = int(c)
            f += Fraction(n, pow(10, i + 1))
        result_fraction += f

    print(f"Generated fraction {result_fraction} from decimal {x}")
    return result_fraction
