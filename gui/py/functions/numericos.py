from __future__ import annotations

import sympy
from typing import Callable

from .utils import latex
from .utils import latparser as parser
from .utils.auxiliar import sympy_expr


def _line(*parts: str) -> None:
    """Append a single LaTeX line to the shared buffer."""
    latex.LATEX_STDOUT.writelatex("".join(parts) + latex.newline())


def _header(title: str, expr: sympy.Expr | None = None) -> None:
    latex.LATEX_STDOUT.clear()
    _line(latex.text(title))
    if expr is not None:
        _line(latex.text("f(x) = "), latex.sympy_expression(expr))


def _format_decimal(num: float) -> str:
    return latex.number_decimal(sympy_expr(num))

# Legacy alias for validation strings


def _format(num: float) -> str:
    return _format_decimal(num)


def _parse_function(raw_expr: str) -> tuple[sympy.Expr, Callable[[float], float]]:
    """
    Parse a LaTeX-like expression into a sympy.Expr and a numeric evaluator.
    """
    x = sympy.symbols("x")
    env = parser.reserved_env.copy()
    env["x"] = x

    parsed = parser.eval_latex(raw_expr, env)
    if not isinstance(parsed, sympy.Expr):
        raise ValueError("La funcion debe ser escalar en x.")

    return parsed, sympy.lambdify(x, parsed, "math")


def _parse_scalar(raw: str) -> float:
    """
    Acepta numeros en texto o LaTeX (\frac12) y los convierte a float.
    """
    try:
        val = parser.eval_latex(raw, parser.reserved_env)
        if isinstance(val, sympy.Expr):
            return float(sympy.N(val))
    except Exception:
        pass

    return float(sympy.N(sympy_expr(raw)))


def _table(headers: list[str], rows: list[list[str]]) -> None:
    """
    Imprime una tabla sencilla en LaTeX usando array.
    """
    colspec = "|" + "|".join("c" for _ in headers) + "|"
    # Escapar % en encabezados
    safe_headers = [h.replace("%", "\\%") for h in headers]
    lines = []
    lines.append(f"\\begin{{array}}{{{colspec}}}")
    lines.append("\\hline ")
    lines.append(" & ".join(safe_headers) + " \\\\")
    lines.append("\\hline ")
    for row in rows:
        lines.append(" & ".join(row) + " \\\\")
    lines.append("\\hline ")
    lines.append("\\end{array}")
    latex.LATEX_STDOUT.writelatex("".join(lines) + latex.newline())


def biseccion(funcion: str, a: str, b: str, tolerancia: str, max_iter: int = 50) -> str:
    expr, f = _parse_function(funcion)
    _header("Metodo de biseccion", expr)

    if max_iter <= 0:
        raise ValueError("El numero maximo de iteraciones debe ser positivo.")

    a_val = _parse_scalar(a)
    b_val = _parse_scalar(b)
    tol = _parse_scalar(tolerancia)

    fa = f(a_val)
    fb = f(b_val)

    if fa * fb > 0:
        raise ValueError(
            f"f(a) y f(b) deben tener signos opuestos. f(a) \\approx {_format(fa)}, f(b) \\approx {_format(fb)}")

    _line(latex.text("Intervalo inicial:"),
          f"a \\approx {_format(a_val)}, b \\approx {_format(b_val)}")

    c_val = a_val
    error = abs(b_val - a_val)
    rows: list[list[str]] = []
    prev_c: float | None = None
    converged = False
    iter_used = 0

    for i in range(1, max_iter + 1):
        c_val = (a_val + b_val) / 2
        fc = f(c_val)
        error = abs(b_val - a_val) / 2
        ea = "-"
        if prev_c is not None:
            ea = _format_decimal(abs(c_val - prev_c))

        _line(
            latex.text(f"Iteracion {i}:"),
            f" a \\approx {_format_decimal(a_val)}, b \\approx {_format_decimal(b_val)}, c \\approx {_format_decimal(c_val)}, ",
            f"f(c) \\approx {_format_decimal(fc)}, error \\approx {_format_decimal(error)}",
        )

        rows.append([
            str(i),
            _format_decimal(a_val),
            _format_decimal(b_val),
            _format_decimal(c_val),
            _format_decimal(error),
            _format_decimal(fa),
            _format_decimal(fb),
            _format_decimal(fc),
            ea if ea != "-" else "-",
        ])

        if abs(fc) < tol or error < tol:
            _line(latex.text(f"Convergencia lograda en {i} iteraciones."))
            converged = True
            iter_used = i
            break

        if fa * fc < 0:
            b_val = c_val
            fb = fc
        else:
            a_val = c_val
            fa = fc
        prev_c = c_val

    if not converged:
        iter_used = max_iter
        _line(latex.text(
            f"No se logro la tolerancia en {max_iter} iteraciones."))

    _table(["i", "xl", "xu", "xr", "Ea", "yl", "yu", "yr", "Ea"], rows)
    _line(latex.text("Raiz aproximada:"),
          f" x \\approx {_format_decimal(c_val)}, |f(x)| \\approx {_format_decimal(f(c_val))}")
    _line(
        latex.text("Criterio de paro:"),
        latex.text(" tolerancia="),
        _format_decimal(tol),
        latex.text(", error="),
        _format_decimal(error),
    )
    status = "si" if converged else "no"
    _line(
        latex.text("Convergencia:"),
        latex.text(f" {status}, iteraciones usadas="),
        f"{iter_used}/{max_iter}",
    )
    return {
        "latex": latex.LATEX_STDOUT.stdout,
        "raiz": float(c_val),
        "f_raiz": float(f(c_val)),
        "converge": converged,
        "iteraciones": iter_used,
    }


def regla_falsa(funcion: str, a: str, b: str, tolerancia: str, max_iter: int = 50) -> str:
    expr, f = _parse_function(funcion)
    _header("Metodo de regula falsi (falsa posicion)", expr)

    if max_iter <= 0:
        raise ValueError("El numero maximo de iteraciones debe ser positivo.")

    a_val = _parse_scalar(a)
    b_val = _parse_scalar(b)
    tol = _parse_scalar(tolerancia)

    fa = f(a_val)
    fb = f(b_val)

    if fa * fb > 0:
        raise ValueError(
            f"f(a) y f(b) deben tener signos opuestos. f(a) \\approx {_format(fa)}, f(b) \\approx {_format(fb)}")

    _line(latex.text("Intervalo inicial:"),
          f" a \\approx {_format(a_val)}, b \\approx {_format(b_val)}")

    c_val = a_val
    error = abs(b_val - a_val)
    rows: list[list[str]] = []
    prev_c: float | None = None
    converged = False
    iter_used = 0

    for i in range(1, max_iter + 1):
        c_val = (a_val * fb - b_val * fa) / (fb - fa)
        fc = f(c_val)
        error = abs(fc)
        ea = "-"
        if prev_c is not None:
            ea = _format_decimal(abs(c_val - prev_c))

        _line(
            latex.text(f"Iteracion {i}:"),
            f" a \\approx {_format_decimal(a_val)}, b \\approx {_format_decimal(b_val)}, xr \\approx {_format_decimal(c_val)}, ",
            f"f(xr) \\approx {_format_decimal(fc)}, error \\approx {_format_decimal(error)}",
        )

        rows.append([
            str(i),
            _format_decimal(a_val),
            _format_decimal(b_val),
            _format_decimal(c_val),
            _format_decimal(error),
            _format_decimal(fa),
            _format_decimal(fb),
            _format_decimal(fc),
            ea if ea != "-" else "-",
        ])

        if abs(fc) < tol or error < tol:
            _line(latex.text(f"Convergencia lograda en {i} iteraciones."))
            converged = True
            iter_used = i
            break

        if fa * fc < 0:
            b_val = c_val
            fb = fc
        else:
            a_val = c_val
            fa = fc
        prev_c = c_val

    if not converged:
        iter_used = max_iter
        _line(latex.text(
            f"No se logro la tolerancia en {max_iter} iteraciones."))

    _table(["i", "xl", "xu", "xr", "Ea", "vl", "vu", "vr", "Ea"], rows)
    _line(latex.text("Raiz aproximada:"),
          f" x \\approx {_format_decimal(c_val)}, |f(x)| \\approx {_format_decimal(f(c_val))}")
    _line(
        latex.text("Criterio de paro:"),
        latex.text(" tolerancia \\approx "),
        _format_decimal(tol),
        latex.text(", error \\approx "),
        _format_decimal(error),
    )
    status = "si" if converged else "no"
    _line(
        latex.text("Convergencia:"),
        latex.text(f" {status}, iteraciones usadas="),
        f"{iter_used}/{max_iter}",
    )
    return {
        "latex": latex.LATEX_STDOUT.stdout,
        "raiz": float(c_val),
        "f_raiz": float(f(c_val)),
        "converge": converged,
        "iteraciones": iter_used,
    }


def _ensure_domain(f: Callable[[float], float], df: Callable[[float], float], xi: float, proposal: float) -> float:
    """
    Intenta que el siguiente punto permanezca en el dominio.
    Si f o f' fallan en el candidato, se aplica un amortiguamiento
    hacia el valor actual hasta 10 veces.
    """
    x_next = proposal
    for _ in range(10):
        try:
            f(x_next)
            df(x_next)
            return x_next
        except ValueError:
            x_next = (x_next + xi) / 2
    raise ValueError(
        f"La funcion no es evaluable en el siguiente valor calculado (x={_format_decimal(proposal)}). "
        "El metodo salto fuera del dominio; intenta una semilla mas cercana a la raiz."
    )


def newton_raphson(funcion: str, x0: str, tolerancia: str, max_iter: int = 50) -> str:
    expr, f = _parse_function(funcion)
    x = sympy.symbols("x")
    deriv = sympy.diff(expr, x)
    df = sympy.lambdify(x, deriv, "math")

    _header("Metodo de Newton-Raphson", expr)
    _line(latex.text("Derivada:"), latex.sympy_expression(deriv))

    xi = _parse_scalar(x0)
    tol = _parse_scalar(tolerancia)
    error = tol

    rows: list[list[str]] = []
    prev_x: float | None = None
    converged = False
    iter_used = 0

    for i in range(1, max_iter + 1):
        try:
            fxi = f(xi)
        except ValueError as exc:
            raise ValueError(
                f"No se pudo evaluar f(x) en x={_format_decimal(xi)}: {exc}")

        try:
            dfxi = df(xi)
        except ValueError as exc:
            raise ValueError(
                f"No se pudo evaluar f'(x) en x={_format_decimal(xi)}: {exc}")

        if dfxi == 0:
            raise ValueError("La derivada es 0; no se puede continuar.")

        x_next = xi - fxi / dfxi
        x_next = _ensure_domain(f, df, xi, x_next)
        error = abs(x_next - xi)

        ea = "-"
        if prev_x is not None:
            ea = _format_decimal(abs(x_next - prev_x))

        _line(
            latex.text(f"Iteracion {i}:"),
            f" xi \\approx {_format_decimal(xi)}, f(xi) \\approx {_format_decimal(fxi)}, f'(xi) \\approx {_format_decimal(dfxi)}, ",
            f"x_{i+1} \\approx {_format_decimal(x_next)}, error \\approx {_format_decimal(error)}",
        )
        rows.append([
            str(i),
            _format_decimal(xi),
            _format_decimal(x_next),
            _format_decimal(error),
            _format_decimal(fxi),
            _format_decimal(dfxi),
        ])

        if abs(fxi) < tol or error < tol:
            xi = x_next
            _line(latex.text(f"Convergencia lograda en {i} iteraciones."))
            converged = True
            iter_used = i
            break

        xi = x_next
        prev_x = xi

    if not converged:
        iter_used = max_iter
        _line(latex.text(
            f"No se logro la tolerancia en {max_iter} iteraciones."))

    _table(["i", "x_i", "x_{i+1}", "Ea", "f(x_i)", "f'(x_i)"], rows)
    _line(latex.text("Raiz aproximada:"),
          f" x \\approx {_format_decimal(xi)}, |f(x)| \\approx {_format_decimal(f(xi))}")
    _line(
        latex.text("Criterio de paro:"),
        latex.text(" tolerancia \\approx "),
        _format_decimal(tol),
        latex.text(", error \\approx "),
        _format_decimal(error),
    )
    status = "si" if converged else "no"
    _line(
        latex.text("Convergencia:"),
        latex.text(f" {status}, iteraciones usadas="),
        f"{iter_used}/{max_iter}",
    )
    return {
        "latex": latex.LATEX_STDOUT.stdout,
        "raiz": float(xi),
        "f_raiz": float(f(xi)),
        "converge": converged,
        "iteraciones": iter_used,
    }


def secante(funcion: str, x0: str, x1: str, tolerancia: str, max_iter: int = 50) -> str:
    expr, f = _parse_function(funcion)
    _header("Metodo de la secante", expr)

    if max_iter <= 0:
        raise ValueError("El numero maximo de iteraciones debe ser positivo.")

    x_prev = _parse_scalar(x0)
    x_curr = _parse_scalar(x1)
    tol = _parse_scalar(tolerancia)

    f_prev = f(x_prev)
    f_curr = f(x_curr)

    _line(latex.text("Semilla inicial:"),
          f" x0 \\approx {_format_decimal(x_prev)}, x1 \\approx {_format_decimal(x_curr)}")

    error = abs(x_curr - x_prev)
    rows: list[list[str]] = []
    prev_x: float | None = None
    converged = False
    iter_used = 0

    for i in range(1, max_iter + 1):
        if f_curr - f_prev == 0:
            raise ValueError("Division por cero en la formula de la secante.")

        x_next = x_curr - f_curr * (x_curr - x_prev) / (f_curr - f_prev)
        error = abs(x_next - x_curr)
        ea = "-"
        if prev_x is not None:
            ea = _format_decimal(abs(x_next - prev_x))

        _line(
            latex.text(f"Iteracion {i}:"),
            f" x_{i-1} \\approx {_format_decimal(x_prev)}, x_{i} \\approx {_format_decimal(x_curr)}, ",
            f"f(x_{i-1}) \\approx {_format_decimal(f_prev)}, f(x_{i}) \\approx {_format_decimal(f_curr)}, ",
            f"x_{i+1} \\approx {_format_decimal(x_next)}, error \\approx {_format_decimal(error)}",
        )
        rows.append([
            str(i),
            _format_decimal(x_prev),
            _format_decimal(x_curr),
            _format_decimal(f_prev),
            _format_decimal(f_curr),
            _format_decimal(x_next),
            _format_decimal(error),
        ])

        if abs(f_curr) < tol or error < tol:
            x_curr = x_next
            _line(latex.text(f"Convergencia lograda en {i} iteraciones."))
            converged = True
            iter_used = i
            break

        x_prev, f_prev = x_curr, f_curr
        x_curr = x_next
        f_curr = f(x_curr)
        prev_x = x_curr

    if not converged:
        iter_used = max_iter
        _line(latex.text(
            f"No se logro la tolerancia en {max_iter} iteraciones."))

    _table(["i", "x_{i-1}", "x_i", "f(x_{i-1})", "f(x_i)", "x_{i+1}", "Ea"], rows)
    _line(latex.text("Raiz aproximada:"),
          f" x \\approx {_format_decimal(x_curr)}, |f(x)| \\approx {_format_decimal(f(x_curr))}")
    _line(
        latex.text("Criterio de paro:"),
        latex.text(" tolerancia \\approx "),
        _format_decimal(tol),
        latex.text(", error \\approx "),
        _format_decimal(error),
    )
    status = "si" if converged else "no"
    _line(
        latex.text("Convergencia:"),
        latex.text(f" {status}, iteraciones usadas="),
        f"{iter_used}/{max_iter}",
    )
    return {
        "latex": latex.LATEX_STDOUT.stdout,
        "raiz": float(x_curr),
        "f_raiz": float(f(x_curr)),
        "converge": converged,
        "iteraciones": iter_used,
    }
