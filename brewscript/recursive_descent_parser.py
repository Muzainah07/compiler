
from pathlib import Path

# Global variables, like the input position in class examples
tokens = []
pos = 0

# Used to report syntax errors
ParserError = SyntaxError


# Get the current token
def current():
    if pos < len(tokens):
        return tokens[pos]
    return None


# Check the current token
def check(*values):
    token = current()

    if token is None:
        return False

    return token.type in values or token.lexeme in values


# Move to the next token
def advance():
    global pos
    pos += 1


# Check whether the expected token is present
def expect(*values):
    token = current()

    if token is not None and (
        token.type in values or token.lexeme in values
    ):
        advance()
    else:
        if token is None:
            raise ParserError(
                f"Syntax error: expected {values}, but reached end of input."
            )

        raise ParserError(
            f"Syntax error at line {token.line}, column {token.col}: "
            f"expected {values}, found {token.lexeme!r}."
        )


# <Program> -> #roast <Program'> 
def Program():
    expect("ROAST", "#roast")

    if check("{"):
        Block()
    else:
        StatementList(("END", "#brew_end"))

    expect("END", "#brew_end")


# <Block> -> { <StmtList> }
def Block():
    expect("{")
    StatementList(("}",))
    expect("}")


# <StmtList> -> <Stmt> <StmtList> | epsilon
def StatementList(stop_tokens):
    while current() is not None and not check(*stop_tokens):
        old_pos = pos
        Statement()

        if pos == old_pos:
            raise ParserError("Parser could not move to the next token.")


# <Stmt> -> declaration | assignment | output | block | condition | loop
def Statement():
    if check("{"):
        Block()

    elif check("DT", "shots", "bean", "blend"):
        Declaration()
        expect(";")

    elif check("PROFILE", "profile"):
        Profile()

    elif check("INFUSE", "infuse"):
        Infuse()

    elif check("OUTPUT", "pull"):
        Output()
        expect(";")

    elif check("ID"):
        Assignment()
        expect(";")

    else:
        token = current()

        if token is None:
            raise ParserError("Unexpected end of input.")

        raise ParserError(
            f"Invalid statement at line {token.line}, "
            f"column {token.col}: {token.lexeme!r}."
        )


# <VarDecl> -> DT <IdList>
def Declaration():
    expect("DT", "shots", "bean", "blend")
    expect("ID")

    while check(","):
        expect(",")
        expect("ID")


# <Assignment> -> ID <Assignment'>
def Assignment():
    expect("ID")

    if check("++", "--"):
        advance()

    elif check("="):
        expect("=")

        if check("INPUT", "barista"):
            Input()
        else:
            Expression()

    elif check("+="):
        expect("+=")
        Expression()

    else:
        raise ParserError(
            "Expected =, +=, ++ or -- after the identifier."
        )


# <OutputStmt> -> pull ( <ArgList> )
def Output():
    expect("OUTPUT", "pull")
    expect("(")

    Expression()

    while check(","):
        expect(",")
        Expression()

    expect(")")


# <InputExpr> -> barista ( TEXT_LITERAL ) | barista ( )
def Input():
    expect("INPUT", "barista")
    expect("(")

    if not check(")"):
        String()

    expect(")")


# A string contains quote, TEXT_LITERAL, quote
def String():
    if check('"'):
        expect('"')
        expect("TEXT_LITERAL")
        expect('"')

    elif check("'"):
        expect("'")
        expect("TEXT_LITERAL")
        expect("'")

    else:
        raise ParserError("Expected a string literal.")


# profile <Expr> ? <Stmt> [adjust ? <Stmt>]
def Profile():
    expect("PROFILE", "profile")
    Expression()
    expect("?")
    Statement()

    if check("ADJUST", "adjust"):
        advance()
        expect("?")
        Statement()


# infuse <Expr> : <Stmt>
def Infuse():
    expect("INFUSE", "infuse")
    Expression()
    expect(":")
    Statement()


# <Expr> -> logical OR expression
def Expression():
    LogicalAnd()

    while check("||"):
        expect("||")
        LogicalAnd()


# Logical AND
def LogicalAnd():
    Relational()

    while check("&&"):
        expect("&&")
        Relational()


# Relational operators
def Relational():
    Addition()

    if check("<", "<=", ">", ">=", "==", "!="):
        advance()
        Addition()


# Addition and subtraction
def Addition():
    Multiplication()

    while check("+", "-"):
        advance()
        Multiplication()


# Multiplication, division and remainder
def Multiplication():
    Unary()

    while check("x", "/", "%"):
        advance()
        Unary()


# Unary operators
def Unary():
    if check("!", "-", "+"):
        advance()
        Unary()
    else:
        Factor()


# <Factor> -> ( <Expr> ) | ID | INT_LITERAL | TEXT_LITERAL
def Factor():
    if check("("):
        expect("(")
        Expression()
        expect(")")

    elif check("ID", "INT_LITERAL"):
        advance()

    elif check("TEXT_LITERAL"):
        advance()

    elif check('"', "'"):
        String()

    else:
        token = current()

        if token is None:
            raise ParserError("Expected a value, but reached end of input.")

        raise ParserError(
            f"Invalid expression at line {token.line}, "
            f"column {token.col}: {token.lexeme!r}."
        )


# Main function called by main.py
def parse_tokens(input_tokens):
    global tokens, pos

    tokens = input_tokens
    pos = 0

    Program()

    if current() is not None:
        token = current()
        raise ParserError(
            f"Unexpected token {token.lexeme!r} "
            f"at line {token.line}, column {token.col}."
        )
