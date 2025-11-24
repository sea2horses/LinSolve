from fractions import Fraction
from enum import Enum
from abc import ABC, abstractmethod
from collections.abc import Callable
from .auxiliar import decimal_a_fraccion, array_top, sympy_expr
from ..models import matriz
from ..models import vector
from ..models.number import Number
from ..operations import operaciones as op
import sympy

type Operand = sympy.Expr | matriz.Matriz | vector.Vector


# Reserved variables
reserved_env: dict[str, Operand | None] = {
    "e": sympy.E,
    "T": None,  # Reserved for transposing
    "t": None,  # Reserved for transposing
    "I": None,  # Reserved for Identity Matrix
}

# TODO:
# Parse lbrack rbrack
# Parse lbrace rbrace
# Parse logarithms
# Parse square roots


class AllowedCommands(Enum):
    frac = 1
    left = 2
    right = 3
    pi = 4
    cdot = 5
    lbrack = 6
    rbrack = 7
    sin = 8
    cos = 9
    tan = 10
    e = 11


command_map: dict[str, AllowedCommands] = {
    "frac": AllowedCommands.frac,
    "left": AllowedCommands.left,
    "right": AllowedCommands.right,
    "pi": AllowedCommands.pi,
    "cdot": AllowedCommands.cdot,
    "lbrack": AllowedCommands.lbrack,
    "rbrack": AllowedCommands.rbrack,
    "sin": AllowedCommands.sin,
    "cos": AllowedCommands.cos,
    "tan": AllowedCommands.tan,
    "e": AllowedCommands.e
}


class TokenType(Enum):
    COMMAND = 1

    # Operators
    SUM = 2
    MINUS = 3
    POW = 4
    SUBSCRIPT = 5

    # Special Characters
    LPARENTHESES = 6
    RPARENTHESES = 7

    # Braces
    LBRACE = 8
    RBRACE = 9

    # Brackets
    LBRACKET = 14
    RBRACKET = 15

    # Other tokens
    DIGIT = 10
    PERIOD = 11

    CHAR = 12

    EOF = 13


class Token:
    def __init__(self, _type: TokenType, value: str | None = None):
        self.type = _type
        self.value: str = value if value is not None else ""

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r})"


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos: int = 0
        self.current_char: str | None = self.text[self.pos] if self.text else None

    def advance(self) -> None:
        self.pos += 1
        self.current_char = self.text[self.pos] if self.text and self.pos < len(
            self.text) else None

    def skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def command(self) -> Token:
        # We are at a backslash, consume '\' then letters
        self.advance()  # skip '\'
        start = self.pos
        while self.current_char is not None and self.current_char.isalpha():
            self.advance()
        cmd = self.text[start:self.pos]
        if cmd not in command_map:
            raise ValueError(f"Unsupported LaTeX command '\\{cmd}'")
        return Token(TokenType.COMMAND, cmd)

    def get_token(self) -> Token:
        while self.current_char is not None and self.current_char.isspace():
            self.skip_whitespace()

        if self.current_char is None:
            return Token(TokenType.EOF)

        if self.current_char.isdigit():
            ch = self.current_char
            self.advance()
            return Token(TokenType.DIGIT, ch)

        if self.current_char.isalpha():
            ch = self.current_char
            self.advance()
            return Token(TokenType.CHAR, ch)

        tok: TokenType | None = None
        match self.current_char:
            case '\\':
                return self.command()
            case '{':
                tok = TokenType.LBRACE
            case '}':
                tok = TokenType.RBRACE
            case '(':
                tok = TokenType.LPARENTHESES
            case ')':
                tok = TokenType.RPARENTHESES
            case '+':
                tok = TokenType.SUM
            case '-':
                tok = TokenType.MINUS
            case '^':
                tok = TokenType.POW
            case '.':
                tok = TokenType.PERIOD
            case '[':
                tok = TokenType.LBRACKET
            case ']':
                tok = TokenType.RBRACKET
            case '_':
                tok = TokenType.SUBSCRIPT
            case _:
                raise ValueError(f"Unrecognized token: {self.current_char}")
        ch = self.current_char
        self.advance()
        # important: store the character itself as `value` (esp. for '.')
        return Token(tok, ch)

    def tokenize(self) -> list[Token]:
        token_list: list[Token] = []

        while self.current_char is not None:
            t = self.get_token()
            if t.type == TokenType.EOF:
                break
            token_list.append(t)

        return token_list


# Clase abstracta
class AST(ABC):
    pass


class ICommandParser(ABC):
    @abstractmethod
    def parsefrac(self) -> AST:
        pass

    @abstractmethod
    def parseleft(self) -> AST:
        pass

    @abstractmethod
    def parseright(self) -> AST:
        pass

    @abstractmethod
    def parsepi(self) -> AST:
        pass


class NumberAST(AST):
    def __init__(self, value: sympy.Expr) -> None:
        self.value: sympy.Expr = value

    def __str__(self) -> str:
        return self.value.__str__()

    def __repr__(self) -> str:
        return f"Number({self.value})"


class VariableAST(AST):
    def __init__(self, id: str) -> None:
        self.id = id

    def __str__(self) -> str:
        return self.id.__str__()

    def __repr__(self) -> str:
        return f"Variable({self.id})"


class Operations(Enum):
    SUM = 1
    SUBTRACT = 2
    MULTIPLY = 3
    DIVIDE = 4
    POWER = 5


allowed_unaries: list[Operations] = [
    Operations.SUBTRACT
]

operation_precedences: dict[Operations, int] = {
    Operations.SUM: 13,
    Operations.SUBTRACT: 13,
    Operations.MULTIPLY: 14,
    Operations.DIVIDE: 14,
    Operations.POWER: 15
}

enclosers: dict[TokenType, TokenType] = {
    TokenType.LPARENTHESES: TokenType.RPARENTHESES,
    TokenType.LBRACE: TokenType.RBRACE,
    TokenType.LBRACKET: TokenType.RBRACKET
}


def precedence(op: Operations) -> int:
    return operation_precedences[op]


class BinOpAST(AST):
    def __init__(self, lhs: AST, op: Operations, rhs: AST) -> None:
        self.lhs: AST = lhs
        self.op: Operations = op
        self.rhs: AST = rhs

    def __repr__(self) -> str:
        return f"BinOp({self.lhs}, {self.op}, {self.rhs})"


class UnaryOpAST(AST):
    def __init__(self, part: AST, op: Operations) -> None:
        if op not in allowed_unaries:
            raise ValueError(f"Operator not allowed as unary: {op}")
        self.op: Operations = op
        self.part: AST = part

    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, {self.part})"


class FunctionDef:
    def __init__(self, arg_count: int, exec: Callable[[list[Operand]], Operand]):
        self.arg_count = arg_count
        self.func = exec

    def execute(self, values: list[Operand]) -> Operand:
        if len(values) != self.arg_count:
            raise Exception("fuck")
        return self.func(values)

    def __repr__(self) -> str:
        return f"Function({self.arg_count}, {self.func!r})"


def sinfunc(args: list[Operand]) -> Operand:
    if not isinstance(args[0], sympy.Expr):
        raise Exception(
            f"La funcion no es válida para objeto de tipo {type(args[0])}")
    return sympy.sin(args[0])  # type: ignore


def cosfunc(args: list[Operand]) -> Operand:
    if not isinstance(args[0], sympy.Expr):
        raise Exception(
            f"La funcion no es válida para objeto de tipo {type(args[0])}")
    return sympy.cos(args[0])  # type: ignore


def tanfunc(args: list[Operand]) -> Operand:
    if not isinstance(args[0], sympy.Expr):
        raise Exception(
            f"La funcion no es válida para objeto de tipo {type(args[0])}")
    return sympy.tan(args[0])  # type: ignore


functions: dict[str, FunctionDef] = {
    "sin": FunctionDef(1, sinfunc),
    "cos": FunctionDef(1, cosfunc),
    "tan": FunctionDef(1, tanfunc)
}


class FunctionAST(AST):
    def __init__(self, name: str, args: list[AST]):
        definition: FunctionDef | None = functions.get(name)

        if definition is None:
            raise Exception(f"Function {name} does not exist.")

        if len(args) != definition.arg_count:
            raise Exception(
                f"Function {name} expected {definition.arg_count} arguments but got {len(args)}")

        self.name = name
        self.args = args


class Parser(ICommandParser):
    def __init__(self, text: str) -> None:
        lexer = Lexer(text)
        self.tokens: list[Token] = lexer.tokenize()
        self.current_pos: int = 0
        self.current_token: Token | None = self.tokens[self.current_pos] if self.tokens and self.current_pos < len(
            self.tokens) else None

    def advance(self) -> None:
        self.current_pos += 1
        self.current_token = self.tokens[self.current_pos] if self.tokens and self.current_pos < len(
            self.tokens) else None

    def eat_token(self, type: TokenType) -> str:
        if self.current_token is None or self.current_token.type != type:
            raise Exception(
                f"Was expecting token of type {type}")
        value = self.current_token.value
        self.advance()

        return value

    def eat_command(self) -> AllowedCommands:
        return command_map[self.eat_token(TokenType.COMMAND)]

    # Operator precedence (checks if an operator exists even)
    def parse_operator(self) -> Operations | None:
        tok = self.current_token
        if tok is None:
            return None

        match tok.type:
            case TokenType.COMMAND:
                cmd = command_map[tok.value]
                if cmd == AllowedCommands.cdot:
                    self.eat_token(TokenType.COMMAND)
                    return Operations.MULTIPLY
            case TokenType.POW:
                self.eat_token(TokenType.POW)
                return Operations.POWER
            case TokenType.SUM:
                self.eat_token(TokenType.SUM)
                return Operations.SUM
            case TokenType.MINUS:
                self.eat_token(TokenType.MINUS)
                return Operations.SUBTRACT
            case _:
                return None

    def starts_operand(self) -> bool:
        tok = self.current_token
        if tok is None:
            return False

        # Simple cases: literals and grouped expressions
        if tok.type in (TokenType.DIGIT,
                        TokenType.CHAR,
                        TokenType.LPARENTHESES,
                        TokenType.LBRACE):
            return True

        # Commands that behave like operands
        if tok.type == TokenType.COMMAND:
            cmd = command_map.get(tok.value)
            return cmd in (
                AllowedCommands.frac,
                AllowedCommands.left,
                AllowedCommands.pi,
                AllowedCommands.e,
                AllowedCommands.sin,
                AllowedCommands.cos,
                AllowedCommands.tan,
            )

        return False

    # Long form argument groups and builds numbers transforming them into their full version
    # Short form operands let stuff like \frac45 consider 4 and 5 as different arguments,
    # long form will group them together to form 45

    def get_token_as_operand(self, long_form: bool = True) -> AST | None:
        tok = self.current_token
        if tok is None:
            return None

        # Check if we're on an operator (Unary parsing)
        op = self.parse_operator()
        if op is not None:
            dest: bool = self.starts_operand()
            if not dest:
                raise Exception("Expected operand after unary operator")
            return UnaryOpAST(self.parse_operand(), op)

        # Commands that behave like operands: \frac, \pi, \left...
        if tok.type == TokenType.COMMAND:
            cmd: AllowedCommands = command_map[tok.value]
            match cmd:
                case AllowedCommands.frac:
                    self.eat_token(TokenType.COMMAND)
                    return self.parsefrac()
                case AllowedCommands.left:
                    self.eat_token(TokenType.COMMAND)
                    return self.parseleft()
                case AllowedCommands.pi:
                    self.eat_token(TokenType.COMMAND)
                    return self.parsepi()
                case AllowedCommands.e:
                    self.eat_token(TokenType.COMMAND)
                    return self.parseE()
                case AllowedCommands.sin:
                    self.eat_token(TokenType.COMMAND)
                    return self.parsesin()
                case AllowedCommands.cos:
                    self.eat_token(TokenType.COMMAND)
                    return self.parsecos()
                case AllowedCommands.tan:
                    self.eat_token(TokenType.COMMAND)
                    return self.parsetan()
                case _:
                    return None

        match tok.type:
            case TokenType.DIGIT:
                if long_form:
                    return self.collapse_number()
                else:
                    d = self.eat_token(TokenType.DIGIT)
                    return NumberAST(sympy_expr(int(d)))

            case TokenType.CHAR:
                c = self.eat_token(TokenType.CHAR)
                return VariableAST(c)

            case TokenType.LPARENTHESES:
                self.eat_token(TokenType.LPARENTHESES)
                expr = self.parse_expression()
                self.eat_token(TokenType.RPARENTHESES)
                return expr

            case TokenType.LBRACE:
                self.eat_token(TokenType.LBRACE)
                expr = self.parse_expression()
                self.eat_token(TokenType.RBRACE)
                return expr

            case _:
                return None

    def parse_operand(self, long_form: bool = True) -> AST:
        r: AST | None = self.get_token_as_operand(long_form)
        if r is None:
            raise Exception("Expected Operand")
        return r

    def collapse_number(self) -> AST:
        chars: list[str] = []

        while (
            self.current_token is not None
            and self.current_token.type in (TokenType.DIGIT, TokenType.PERIOD)
        ):
            chars.append(self.current_token.value)
            self.advance()

        num_str = "".join(chars)      # e.g. "12.5"
        frac = sympy_expr(num_str)
        return NumberAST(frac)

    def parsefrac(self) -> AST:
        """
        Assumes '\\frac' has already been consumed.

        Supports:
            - \\frac12  (short form: single-digit operands)
            - \\frac{1}{2}  (long form: full expressions)
        """

        numerator = self.parse_operand(long_form=False)
        denominator = self.parse_operand(long_form=False)

        return BinOpAST(numerator, Operations.DIVIDE, denominator)

    def parsepi(self) -> AST:
        return NumberAST(sympy.pi)

    def parseE(self) -> AST:
        return NumberAST(sympy.E)

    def parseleft(self) -> AST:
        """
        Parse \\left( expr \\right) style groups.
        Assumes 'left' command has already been consumed.
        """
        if self.current_token is None or self.current_token.type != TokenType.LPARENTHESES:
            raise Exception("Expected encloser after \\left")

        right_encloser: TokenType | None = enclosers.get(
            self.current_token.type)

        if right_encloser is None:
            raise Exception(f"Token is not a valid encloser")

        self.advance()
        expr = self.parse_expression()

        # Right command
        m = self.eat_command()
        if m != AllowedCommands.right:
            raise Exception("Expected \\right directive")

        self.eat_token(right_encloser)
        return expr

    def parseright(self) -> AST:
        # Bare \right shouldn't really appear as an operand: treat as no-op.
        raise Exception("\\right without \\left directive")

    def parsesin(self) -> AST:
        return FunctionAST("sin", [self.parse_operand()])

    def parsecos(self) -> AST:
        return FunctionAST("cos", [self.parse_operand()])

    def parsetan(self) -> AST:
        return FunctionAST("tan", [self.parse_operand()])

    def expr_to_postfix(self) -> list[AST | Operations]:
        opstack: list[Operations] = []
        totalstack: list[AST | Operations] = []

        # Obligatory first operand
        totalstack.append(self.parse_operand())

        m: Operations | None = self.parse_operator()
        while True:
            if m is None:
                if not self.starts_operand():
                    break
                # Implicit multiplication
                m = Operations.MULTIPLY

            while len(opstack) != 0 and precedence(m) <= precedence(array_top(opstack)):
                last = opstack.pop()
                totalstack.append(last)
            opstack.append(m)

            totalstack.append(self.parse_operand())

            m = self.parse_operator()

        while len(opstack) != 0:
            totalstack.append(opstack.pop())

        return totalstack

    def postfix_parse(self, postfix: list[AST | Operations]) -> AST:
        stack: list[AST] = []
        for item in postfix:
            if isinstance(item, AST):
                stack.append(item)
            else:
                # binary op: pop right then left
                if len(stack) < 2:
                    raise Exception("Invalid postfix expression")
                rhs = stack.pop()
                lhs = stack.pop()
                stack.append(BinOpAST(lhs, item, rhs))

        if len(stack) != 1:
            raise Exception("Invalid postfix expression")

        return stack[0]

    def parse_expression(self) -> AST:
        return self.postfix_parse(self.expr_to_postfix())

# ===== Evaluator =====


type OperationHandler = Callable[[Operand, Operand], Operand]

type HandlerDictionary = dict[tuple[type, type], OperationHandler]


def _dispatch(a: Operand, b: Operand, handlers: HandlerDictionary) -> Operand:
    """
    Simple dispatcher: handlers keys: 'scalar_scalar', 'mat_mat', 'vec_vec',
    'mat_scalar', 'scalar_mat'. Raise readable error on unsupported pair.
    """

    qualified_handler: OperationHandler | None = None

    # Check for actual order first
    for (t1, t2), h in handlers.items():
        if isinstance(a, t1) and isinstance(b, t2):
            qualified_handler = h

    if qualified_handler is not None:
        return qualified_handler(a, b)

    for (t1, t2), h in handlers.items():
        if isinstance(b, t1) and isinstance(a, t2):
            qualified_handler = h

    if qualified_handler is not None:
        return qualified_handler(b, a)

    raise Exception(
        f"Operación no soportada para tipos {type(a)} y {type(b)}")

# fmt: off

def generic_sum(a: Operand, b: Operand) -> Operand:
    return _dispatch(a, b, {
        (sympy.Expr, sympy.Expr): lambda x, y: x + y, # type: ignore
        (matriz.Matriz, matriz.Matriz): lambda x, y: op.suma_matrices(x, y), # type: ignore
        (vector.Vector, vector.Vector): lambda x, y: op.suma_vectores(x, y), # type: ignore
        # other combinations are not meaningful for sum
    })


def generic_subtraction(a: Operand, b: Operand) -> Operand:
    return _dispatch(a, b, {
        (sympy.Expr, sympy.Expr): lambda x, y: x - y, # type: ignore
        (matriz.Matriz, matriz.Matriz): lambda x, y: op.resta_matrices(x, y), # type: ignore
        (vector.Vector, vector.Vector): lambda x, y: op.resta_vectores(x, y), # type: ignore
    })


def generic_multiplication(a: Operand, b: Operand) -> Operand:
    return _dispatch(a, b, {
        (sympy.Expr, sympy.Expr): lambda x, y: x * y, # type: ignore
        (matriz.Matriz, matriz.Matriz): lambda x, y: op.multiplicar_matrices(x, y), # type: ignore
        (matriz.Matriz, vector.Vector): lambda x, y: op.matriz_por_vector(x, y), # type: ignore
        (matriz.Matriz, sympy.Expr): lambda x, y: op.matriz_por_escalar(x, y), # type: ignore
        (vector.Vector, sympy.Expr): lambda x, y: op.vector_por_escalar(x, y), # type: ignore
    })

def generic_division(a: Operand, b: Operand) -> Operand:
    return _dispatch(a, b, {
        (sympy.Expr, sympy.Expr): lambda x, y: x / y, # type: ignore
        (matriz.Matriz, matriz.Matriz): lambda x, y: op.multiplicar_matrices(x, op.matriz_inversa(y)), # type: ignore
        # (matriz.Matriz, vector.Vector): lambda x, y: op.matriz_por_vector(x, y), # type: ignore
        (matriz.Matriz, sympy.Expr): lambda x, y: op.matriz_por_escalar(x, sympy_expr(1) / y), # type: ignore
        (vector.Vector, sympy.Expr): lambda x, y: op.vector_por_escalar(x, sympy_expr(1) / y), # type: ignore
    })

def generic_power(a: Operand, b: Operand) -> Operand:
    return _dispatch(a, b, {
        (sympy.Expr, sympy.Expr): lambda x, y: x ** y, # type: ignore
    })

# fmt: on


def generic_negation(a: Operand) -> Operand:
    if isinstance(a, sympy.Expr):
        return -a  # type: ignore
    if isinstance(a, matriz.Matriz):
        return op.matriz_por_escalar(a, sympy_expr(-1))  # type: ignore
    if isinstance(a, vector.Vector):
        return op.vector_por_escalar(a, sympy_expr(-1))  # type: ignore

    raise Exception(f"No se puede negar objeto de tipo {type(a)}")


def generic_inversion(a: Operand) -> Operand:
    if isinstance(a, sympy.Expr):
        return 1/a  # type: ignore
    if isinstance(a, matriz.Matriz):
        return op.matriz_inversa(a)

    raise Exception(f"No se puede invertir objeto de tipo {type(a)}")


def generic_transpose(a: Operand) -> Operand:
    if isinstance(a, matriz.Matriz):
        return op.transponer_matriz(a)
    if isinstance(a, vector.Vector):
        return op.transponer_vector(a)

    raise Exception(f"No se puede invertir objeto de tipo {type(a)}")


def eval_ast(node: AST, env: dict[str, Operand | None]) -> Operand:
    """
    Evaluate an AST into a Python Fraction.

    env: optional mapping from variable name -> Fraction
    """

    # Numbers
    if isinstance(node, NumberAST):
        return node.value

    # Variables
    if isinstance(node, VariableAST):
        if node.id in env:
            val = env.get(node.id)
            if val is None:
                raise Exception(f"Reserved keyword: {val}")
            return val
        raise ValueError(f"Unknown variable '{node.id}' in expression")

    # Functions
    if isinstance(node, FunctionAST):
        eval_args: list[Operand] = list(eval_ast(n, env) for n in node.args)
        f: FunctionDef = functions[node.name]
        return f.execute(eval_args)

    # Unary operators
    if isinstance(node, UnaryOpAST):
        val = eval_ast(node.part, env)
        if node.op == Operations.SUBTRACT:
            return generic_negation(val)
        raise ValueError(f"Unsupported unary operation {node.op}")

    # Binary ops
    if isinstance(node, BinOpAST):
        left = eval_ast(node.lhs, env)
        right = eval_ast(node.rhs, env)

        if node.op == Operations.SUM:
            return generic_sum(left, right)
        if node.op == Operations.SUBTRACT:
            return generic_subtraction(left, right)
        if node.op == Operations.MULTIPLY:
            return generic_multiplication(left, right)
        if node.op == Operations.DIVIDE:
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return generic_division(left, right)
        if node.op == Operations.POWER:
            # Pattern for transposing
            if isinstance(node.rhs, VariableAST) and node.rhs.id in ("T", "t"):
                return generic_transpose(left)
            # Pattern for inversion
            if isinstance(node.rhs, NumberAST) and right == -1:
                return generic_inversion(left)
            # Normal power
            return generic_power(left, right)

        raise ValueError(f"Unsupported binary operation {node.op}")

    raise TypeError(f"Unknown AST node type: {type(node)}")


# Alguien mateme mateme pero a las de ya
def dump_ast(node: AST, indent: int = 0, label: str | None = None) -> None:
    """Generic AST pretty-printer using reflection."""
    pad = "  " * indent
    node_type = type(node).__name__

    # Optional label (e.g. attribute name)
    prefix = f"{label}: " if label else ""
    print(f"{pad}{prefix}{node_type}")

    # Now recurse into children
    for attr_name, value in vars(node).items():
        # Single child node
        if isinstance(value, AST):
            dump_ast(value, indent + 1, attr_name)

        # List of child nodes
        elif isinstance(value, list) and value and all(isinstance(v, AST) for v in value):
            print(f"{pad}  {attr_name}:")
            for child in value:
                dump_ast(child, indent + 2)

        else:
            print(f"{pad}  {attr_name}: {value}")


def eval_latex(expr: str, env: dict[str, Operand | None] | None) -> Operand:
    """
    Convenience: parse a LaTeX-ish expression and evaluate to a Fraction.
    """
    parser = Parser(expr)
    ast = parser.parse_expression()

    if env is None:
        env = reserved_env

    print(f"Generated AST from expression: {expr}")
    dump_ast(ast)
    return eval_ast(ast, env)
