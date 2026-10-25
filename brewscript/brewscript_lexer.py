import re
import sys

LIMITS = {
    "MAX_NUM_DIGITS": 8,
    "MAX_ID_LENGTH": 32,
}

BLOCK_COMMENT_OPEN = "/*"
BLOCK_COMMENT_CLOSE = "*/"

KEYWORDS = {
    "shots": "DT",
    "bean": "DT",
    "blend": "DT",
    "infuse": "INFUSE",
    "profile": "PROFILE",
    "adjust": "ADJUST",
    "barista": "INPUT",
    "pull": "OUTPUT",
}

HASH_KEYWORDS = {
    "#roast": "ROAST",
    "#brew_end": "END",
}

MULTI_CHAR_OPERATORS = [
    "==", "!=", "<=", ">=", "&&", "||", "++", "--", "+=", "-=",
]

SINGLE_CHAR_OPERATORS = set("+-x/%<>!=")
SPECIAL_CHARS = set("#{}[],=-()':?;_")

IDENTIFIER_START_RE = re.compile(r"[a-zA-Z_]")
IDENTIFIER_BODY_RE = re.compile(r"[a-zA-Z0-9_]")
DIGIT_RE = re.compile(r"[0-9]")


class Token:
    __slots__ = ("type", "lexeme", "line", "col")

    def __init__(self, type_, lexeme, line, col):
        self.type = type_
        self.lexeme = lexeme
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type!r}, {self.lexeme!r}, line={self.line}, col={self.col})"


class LexicalError:
    __slots__ = ("category", "message", "line", "col", "lexeme")

    def __init__(self, category, message, line, col, lexeme=""):
        self.category = category
        self.message = message
        self.line = line
        self.col = col
        self.lexeme = lexeme

    def __repr__(self):
        loc = f"line {self.line}, col {self.col}"
        lex = f" ({self.lexeme!r})" if self.lexeme else ""
        return f"[{self.category}] {self.message}{lex} @ {loc}"


class Lexer:
    def __init__(self, source: str):
        self.src = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.n = len(source)
        self.tokens = []
        self.errors = []

    def _peek(self, offset=0):
        i = self.pos + offset
        return self.src[i] if i < self.n else ""

    def _advance(self):
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _at_end(self):
        return self.pos >= self.n

    def _starts_with(self, s):
        return self.src.startswith(s, self.pos)

    def tokenize(self):
        while not self._at_end():
            self._dispatch()
        return self.tokens, self.errors

    def _dispatch(self):
        ch = self._peek()

        if ch in (" ", "\t", "\r", "\n"):
            self._advance()
            return

        if self._starts_with(BLOCK_COMMENT_OPEN):
            self._scan_block_comment()
            return

        if ch == "#":
            self._scan_hash()
            return

        if ch in ("'", '"'):
            self._scan_string(ch)
            return

        if IDENTIFIER_START_RE.match(ch):
            self._scan_identifier_or_keyword()
            return

        if DIGIT_RE.match(ch):
            self._scan_number()
            return
        if ch in ("+", "-") and DIGIT_RE.match(self._peek(1)) and self._prev_allows_signed_number():
            self._scan_number()
            return

        for op in MULTI_CHAR_OPERATORS:
            if self._starts_with(op):
                self._scan_operator(op)
                return
        if ch in SINGLE_CHAR_OPERATORS:
            self._scan_operator(ch)
            return

        if ch in SPECIAL_CHARS:
            line, col = self.line, self.col
            self._advance()
            self.tokens.append(Token(ch, ch, line, col))
            return

        self._illegal_character()

    def _prev_allows_signed_number(self):
        if not self.tokens:
            return True
        prev = self.tokens[-1].type
        return prev not in ("ID", "INT_LITERAL", "TEXT_LITERAL", ")")

    def _illegal_character(self):
        line, col = self.line, self.col
        ch = self._advance()
        self.errors.append(LexicalError(
            "Illegal/Invalid Character",
            "character is not part of the BrewScript language",
            line, col, ch,
        ))

    def _scan_hash(self):
        line, col = self.line, self.col
        for lexeme, ttype in HASH_KEYWORDS.items():
            if self._starts_with(lexeme):
                for _ in lexeme:
                    self._advance()
                self.tokens.append(Token(ttype, lexeme, line, col))
                return
        self._skip_line_comment()

    def _skip_line_comment(self):
        self._advance()
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _scan_block_comment(self):
        line, col = self.line, self.col
        self._advance()
        self._advance()
        while not self._at_end():
            if self._starts_with(BLOCK_COMMENT_CLOSE):
                self._advance()
                self._advance()
                return
            self._advance()
        self.errors.append(LexicalError(
            "Unclosed Comment",
            "multi-line comment opened with '/*' is never closed with '*/'",
            line, col, BLOCK_COMMENT_OPEN,
        ))

    def _scan_string(self, quote_char):
        line, col = self.line, self.col
        self.tokens.append(Token(quote_char, quote_char, line, col))
        self._advance()

        content_start_line, content_start_col = self.line, self.col
        content = []
        while not self._at_end() and self._peek() != quote_char and self._peek() != "\n":
            content.append(self._advance())

        if self._at_end() or self._peek() == "\n":
            self.errors.append(LexicalError(
                "Unterminated String/Char",
                f"literal opened with {quote_char!r} is never closed",
                line, col, "".join(content),
            ))
            return

        self.tokens.append(Token("TEXT_LITERAL", "".join(content),
                                  content_start_line, content_start_col))
        close_line, close_col = self.line, self.col
        self._advance()
        self.tokens.append(Token(quote_char, quote_char, close_line, close_col))

    def _scan_identifier_or_keyword(self):
        line, col = self.line, self.col
        lexeme = []
        while not self._at_end() and IDENTIFIER_BODY_RE.match(self._peek()):
            lexeme.append(self._advance())
        text = "".join(lexeme)

        if len(text) > LIMITS["MAX_ID_LENGTH"]:
            self.errors.append(LexicalError(
                "Exceeding Limit",
                f"identifier longer than {LIMITS['MAX_ID_LENGTH']} characters",
                line, col, text,
            ))
            return

        if text in KEYWORDS:
            self.tokens.append(Token(KEYWORDS[text], text, line, col))
        elif text in HASH_KEYWORDS.values():
            self.tokens.append(Token(text, text, line, col))
        else:
            self.tokens.append(Token("ID", text, line, col))

    def _scan_number(self):
        line, col = self.line, self.col
        lexeme = []
        if self._peek() in ("+", "-"):
            lexeme.append(self._advance())
        while not self._at_end() and DIGIT_RE.match(self._peek()):
            lexeme.append(self._advance())

        if not self._at_end() and (self._peek().isalpha() or self._peek() == "_"):
            while not self._at_end() and IDENTIFIER_BODY_RE.match(self._peek()):
                lexeme.append(self._advance())
            text = "".join(lexeme)
            self.errors.append(LexicalError(
                "Invalid Identifier",
                "identifier does not match the identifier RE "
                "(must start with a letter or underscore)",
                line, col, text,
            ))
            return

        text = "".join(lexeme)
        digit_count = len(text.lstrip("+-"))
        if digit_count > LIMITS["MAX_NUM_DIGITS"]:
            self.errors.append(LexicalError(
                "Exceeding Limit",
                f"numeric constant longer than {LIMITS['MAX_NUM_DIGITS']} digits",
                line, col, text,
            ))
            return

        self.tokens.append(Token("INT_LITERAL", text, line, col))

    def _scan_operator(self, op):
        line, col = self.line, self.col
        for _ in op:
            self._advance()
        self.tokens.append(Token(op, op, line, col))


def lex(source: str):
    return Lexer(source).tokenize()


def print_report(source: str):
    tokens, errors = lex(source)

    print(f"{'Lexeme':<25}{'Token':<15}Line:Col")
    print("-" * 55)
    for t in tokens:
        print(f"{t.lexeme:<25}{t.type:<15}{t.line}:{t.col}")

    print()
    if errors:
        print(f"{len(errors)} lexical error(s) found:")
        for e in errors:
            print("  " + repr(e))
    else:
        print("No lexical errors found.")


def read_program():
    print("Type your BrewScript code. Type END on its own line to check it, or quit to exit.")
    lines = []
    while True:
        try:
            line = input("> " if not lines else "  ")
        except EOFError:
            return None if not lines else "\n".join(lines)
        if not lines and line.strip().lower() == "quit":
            return None
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def interactive():
    while True:
        src = read_program()
        if src is None:
            break
        if src.strip():
            print()
            print_report(src)
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            print_report(f.read())
    else:
        interactive()