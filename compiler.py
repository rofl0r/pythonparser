# Token types
TT_EOF = 0
TT_NUMBER = 1
TT_PLUS = 2
TT_MINUS = 3
TT_MULT = 4
TT_DIV = 5
TT_MOD = 6
TT_LPAREN = 7
TT_RPAREN = 8
TT_SEMI = 9
TT_ASSIGN = 10
TT_IDENT = 11
TT_IF = 12
TT_ELSE = 13
TT_END = 14
TT_PRINT = 15
TT_EQ = 16
TT_NE = 17
TT_GE = 18
TT_LE = 19
TT_AND = 20
TT_OR = 21
TT_NOT = 22
TT_BITAND = 23
TT_BITOR = 24
TT_BITNOT = 25
TT_XOR = 26
TT_COLON = 27

# Global precedence table for binary operators
BINARY_PRECEDENCE = {
    TT_OR: 10,      # lowest precedence
    TT_AND: 20,
    TT_BITOR: 30,
    TT_XOR: 40,
    TT_BITAND: 50,
    TT_EQ: 60,
    TT_NE: 60,
    TT_GE: 60,
    TT_LE: 60,
    TT_PLUS: 70,
    TT_MINUS: 70,
    TT_MULT: 80,
    TT_DIV: 80,
    TT_MOD: 80,
}

# Unary operator precedence (higher than binary operators)
UNARY_PRECEDENCE = 90

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token(%d, %s)' % (self.type, self.value)

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        start = self.pos
        while self.current_char and self.current_char.isdigit():
            self.advance()
        return Token(TT_NUMBER, int(self.text[start:self.pos]))

    def identifier(self):
        start = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            self.advance()
        value = self.text[start:self.pos]
        if value == 'if':
            return Token(TT_IF, value)
        elif value == 'else':
            return Token(TT_ELSE, value)
        elif value == 'end':
            return Token(TT_END, value)
        elif value == 'print':
            return Token(TT_PRINT, value)
        elif value == 'and':
            return Token(TT_AND, value)
        elif value == 'or':
            return Token(TT_OR, value)
        return Token(TT_IDENT, value)

    def next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            if self.current_char == '+':
                self.advance()
                return Token(TT_PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(TT_MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(TT_MULT, '*')

            if self.current_char == '/':
                self.advance()
                return Token(TT_DIV, '/')

            if self.current_char == '%':
                self.advance()
                return Token(TT_MOD, '%')

            if self.current_char == '(':
                self.advance()
                return Token(TT_LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(TT_RPAREN, ')')

            if self.current_char == ';':
                self.advance()
                return Token(TT_SEMI, ';')

            if self.current_char == ':':
                self.advance()
                return Token(TT_COLON, ':')

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TT_EQ, '==')
                return Token(TT_ASSIGN, '=')

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TT_NE, '!=')
                return Token(TT_NOT, '!')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TT_GE, '>=')
                self.error()

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TT_LE, '<=')
                self.error()

            if self.current_char == '&':
                self.advance()
                return Token(TT_BITAND, '&')

            if self.current_char == '|':
                self.advance()
                return Token(TT_BITOR, '|')

            if self.current_char == '~':
                self.advance()
                return Token(TT_BITNOT, '~')

            if self.current_char == '^':
                self.advance()
                return Token(TT_XOR, '^')

            self.error()

        return Token(TT_EOF, None)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()

    def error(self, message):
        raise Exception(message)

    def advance(self):
        self.token = self.lexer.next_token()

    def consume(self, token_type):
        if self.token.type == token_type:
            self.advance()
        else:
            self.error('Expected token type %d' % token_type)

    def lbp(self, t):
        return BINARY_PRECEDENCE.get(t.type, 0)

    def expression(self, rbp=0):
        t = self.token
        self.advance()
        if t.type in [TT_MINUS, TT_NOT, TT_BITNOT]:  # Unary operators
            right = self.expression(UNARY_PRECEDENCE)
            return ('UNARY', t.value, right)
        left = self.nud(t)
        while rbp < self.lbp(self.token):
            t = self.token
            self.advance()
            left = self.led(t, left)
        return left

    def nud(self, t):
        if t.type == TT_NUMBER:
            return ('NUM', t.value)
        if t.type == TT_IDENT:
            return ('VAR', t.value)
        if t.type == TT_LPAREN:
            expr = self.expression(0)
            self.consume(TT_RPAREN)
            return expr
        raise Exception('Unexpected token type %d' % t.type)

    def led(self, t, left):
        if t.type in [TT_PLUS, TT_MINUS, TT_MULT, TT_DIV, TT_MOD]:
            return ('BINOP', t.value, left, self.expression(self.lbp(t)))
        elif t.type in [TT_EQ, TT_NE, TT_GE, TT_LE]:
            return ('COMPARE', t.value, left, self.expression(self.lbp(t)))
        elif t.type in [TT_AND, TT_OR]:
            return ('LOGICAL', t.value, left, self.expression(self.lbp(t)))
        elif t.type in [TT_XOR, TT_BITOR, TT_BITAND]:
            return ('BITOP', t.value, left, self.expression(self.lbp(t)))
        raise Exception('Unexpected token type %d' % t.type)

    def statement(self):
        if self.token.type == TT_IF:
            self.advance()
            condition = self.expression(0)
            self.consume(TT_COLON)
            then_body = []
            while self.token.type not in [TT_ELSE, TT_END]:
                then_body.append(self.statement())
            if self.token.type == TT_ELSE:
                self.advance()
                else_body = []
                while self.token.type != TT_END:
                    else_body.append(self.statement())
                self.consume(TT_END)
                return ('IF', condition, then_body, else_body)
            self.consume(TT_END)
            return ('IF', condition, then_body, None)
        elif self.token.type == TT_PRINT:
            self.advance()
            expr = self.expression(0)
            self.consume(TT_SEMI)
            return ('PRINT', expr)
        elif self.token.type == TT_IDENT:
            var = self.token.value
            self.advance()
            if self.token.type == TT_ASSIGN:
                self.advance()
                expr = self.expression(0)
                self.consume(TT_SEMI)
                return ('ASSIGN', var, expr)
        self.error('Invalid statement')

    def parse(self):
        statements = []
        while self.token.type != TT_EOF:
            statements.append(self.statement())
        return statements

def evaluate(node, env):
    if isinstance(node, tuple):
        if node[0] == 'NUM':
            return node[1]
        elif node[0] == 'VAR':
            return env.get(node[1], 0)
        elif node[0] == 'BINOP':
            left = evaluate(node[2], env)
            right = evaluate(node[3], env)
            op = node[1]
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': return left // right
            elif op == '%': return left % right
        elif node[0] == 'UNARY':
            right = evaluate(node[2], env)
            op = node[1]
            if op == '-': return -right
            elif op == '!': return 0 if right else 1
            elif op == '~': return ~right
        elif node[0] == 'ASSIGN':
            value = evaluate(node[2], env)
            env[node[1]] = value
            return value
        elif node[0] == 'PRINT':
            value = evaluate(node[1], env)
            print(value)
            return value
        elif node[0] == 'IF':
            condition = evaluate(node[1], env)
            if condition:
                for stmt in node[2]:
                    evaluate(stmt, env)
            elif node[3]:  # else block exists
                for stmt in node[3]:
                    evaluate(stmt, env)
        elif node[0] == 'COMPARE':
            left = evaluate(node[2], env)
            right = evaluate(node[3], env)
            op = node[1]
            if op == '==': return 1 if left == right else 0
            elif op == '!=': return 1 if left != right else 0
            elif op == '>=': return 1 if left >= right else 0
            elif op == '<=': return 1 if left <= right else 0
        elif node[0] == 'LOGICAL':
            left = evaluate(node[2], env)
            op = node[1]
            if op == 'and':
                return 1 if left and evaluate(node[3], env) else 0
            elif op == 'or':
                return 1 if left or evaluate(node[3], env) else 0
        elif node[0] == 'BITOP':
            left = evaluate(node[2], env)
            right = evaluate(node[3], env)
            op = node[1]
            if op == '&': return left & right
            elif op == '|': return left | right
            elif op == '^': return left ^ right
    return 0

def run(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    program = parser.parse()
    env = {}
    for node in program:
        evaluate(node, env)
    return env

def test():
    test_cases = [
        "x = 5 + 3 * 2; print x;",
        "x = 1; if x == 1: print x; end",
        "x = 1; if x == 1: print x; else: print 0; end",
        "x = 5 | 3; print x;",
        "x = 5 & 3; print x;",
        "x = 5 | 3; y = x & 2; print y;",
        "x = 1; y = 0; if x and y: print x; end",
        "x = 15; y = ~3; print y;",
        "x = 1; if !x or x and y: print x; end",
        "x = 5 ^ 3; print x;",
        "x = -5; print x;",
    ]
    for i, test in enumerate(test_cases):
        print("\nTest %d:" % (i + 1))
        print("Input: %s" % test)
        env = run(test)
        print("Environment: %s" % env)

if __name__ == '__main__':
    test()
