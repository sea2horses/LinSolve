from ..models.matriz import Matriz
from ..models.vector import Vector
from ..models.number import Number
from .auxiliar import sympy_expr
from fractions import Fraction
import re
import sympy


class LatexBuffer():
    stdout = ""

    def __init__(self) -> None:
        pass

    def clear(self) -> None:
        self.stdout = ""

    def write(self, msg: str) -> None:
        self.stdout += text(msg)

    def writeln(self, msg: str) -> None:
        self.stdout += text(msg) + newline()

    def writelatex(self, latex: str) -> None:
        self.stdout += latex


LATEX_STDOUT = LatexBuffer()


def number_parse(n: Number) -> str:
    return sympy_expression(sympy_expr(n))


def sympy_expression(expr: sympy.Expr) -> str:
    return " " + sympy.latex(expr) + " "  # type: ignore


def number_decimal(expr: sympy.Expr | float, precision: int = 8) -> str:
    try:
        val = float(sympy.N(expr, precision))
        formatted = f"{val:.{precision}f}".rstrip("0").rstrip(".")
        return f" {formatted} "
    except Exception:
        return sympy_expression(sympy_expr(expr))


def fraction(frac: Fraction, force_sign: bool = False) -> str:
    latex = ""

    if force_sign and frac >= 0:
        latex += "+"

    if frac.denominator == 1:
        latex += str(frac.numerator)
    else:
        if frac < 0:
            latex += "-"
        latex += f"\\frac{{ {abs(frac.numerator)} }}{{ {frac.denominator} }}"

    return latex


def matrix(mat: Matriz) -> str:

    latex = "\\left[\\begin{array}"

    # Calcular linea
    if mat.linea != -1 and mat.linea < mat.columnas:
        lc = "c" * mat.linea
        rc = "c" * (mat.columnas - mat.linea)
        latex += "{" + lc + "|" + rc + "}"
    else:
        latex += "{" + "c" * mat.columnas + "}"

    # Meter todos los elementos
    for i in range(1, mat.filas + 1):
        for j in range(1, mat.columnas + 1):
            if j != 1:
                latex += " & "
            latex += sympy_expression(mat.at(i, j))
        latex += "\\\\"

    # Terminar
    latex += "\\end{array}\\right]"
    return latex


def vector(vec: Vector) -> str:
    # Construye un vector columna separando con doble backslash correcto
    body = " \\\\ ".join(sympy_expression(c) for c in vec.componentes)
    return "\\begin{bmatrix}" + body + "\\end{bmatrix}"


# Mapping per latex table
_LATEX_MAP = {
    '#': r'\#',
    '$': r'\$',
    '%': r'\%',
    '&': r'\&',
    '~': r'\~{}',       # \~ is an accent; {} makes it a standalone tilde
    '_': r'\_',
    '^': r'\^{}',       # same idea for caret
    '{': r'\{',
    '}': r'\}',
    '>': r'$>$',
    '<': r'$<$',
    '\\': r'$\backslash$',
}

# Match any of the target characters (note the escaped backslash at the end)
_PATTERN = re.compile(r'[#$%&~_^{}><\\]')


def sanitize_text(raw_text: str) -> str:
    return _PATTERN.sub(lambda m: _LATEX_MAP[m.group(0)], raw_text)


def text(msg: str) -> str:
    lines = msg.splitlines()

    latex = ""
    for i, line in enumerate(lines):
        if i != 0:
            latex += newline()
        latex += "\\text{" + sanitize_text(line) + "}"

    return latex


def newline() -> str:
    return "\\\\ "

# Notation stuff


def superscript(msg: str) -> str:
    return "^{" + msg + "}"


def subscript(msg: str) -> str:
    return "_{" + msg + "}"


def cdot() -> str:
    return "\\cdot "


def frac(num: str, den: str) -> str:
    return "\\frac{" + num + "}{" + den + "}"


def larrow() -> str:
    return "\\gets "


def rarrow() -> str:
    return "\\to "


def barrow() -> str:
    return "\\leftrightarrow "


def term(varname: str, coefficent: Number = sympy_expr(1), forcesign: bool = False, hideOne: bool = True, ignoreZero: bool = False) -> str:
    if coefficent == 0 and ignoreZero:
        return ""

    latex = ""
    if forcesign and coefficent >= 0:
        latex += "+"

    if coefficent != 1 or not hideOne:
        latex += number_parse(coefficent)

    latex += varname
    return latex


def indexedvar(varname: str, index: int) -> str:
    return varname + "_{" + str(index) + "} "
