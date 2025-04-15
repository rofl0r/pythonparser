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
TT_DO = 27

# Global hashtable for keywords
KEYWORDS = {
    'if': TT_IF,
    'else': TT_ELSE,
    'end': TT_END,
    'print': TT_PRINT,
    'and': TT_AND,
    'or': TT_OR,
    'do': TT_DO  # Added 'do' keyword
}

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

        # Map of characters to their respective handler methods
        self.op_map = {
            '+': self.handle_plus,
            '-': self.handle_minus,
            '*': self.handle_mult,
            '/': self.handle_div,
            '%': self.handle_mod,
            '(': self.handle_lparen,
            ')': self.handle_rparen,
            ';': self.handle_semi,
            # ':': self.handle_colon,  # Removed colon handler
            '=': self.handle_assign_or_eq,
            '!': self.handle_not_or_ne,
            '>': self.handle_ge,
            '<': self.handle_le,
            '&': self.handle_bitand,
            '|': self.handle_bitor,
            '~': self.handle_bitnot,
            '^': self.handle_xor,
        }

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
        """Parse an identifier or keyword using the global KEYWORDS hashtable"""
        start = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            self.advance()
        value = self.text[start:self.pos]

        # Look up in the global KEYWORDS hashtable, default to TT_IDENT if not found
        token_type = KEYWORDS.get(value, TT_IDENT)
        return Token(token_type, value)

    # Handlers for various operators
    def handle_plus(self):
        self.advance()
        return Token(TT_PLUS, '+')

    def handle_minus(self):
        self.advance()
        return Token(TT_MINUS, '-')

    def handle_mult(self):
        self.advance()
        return Token(TT_MULT, '*')

    def handle_div(self):
        self.advance()
        return Token(TT_DIV, '/')

    def handle_mod(self):
        self.advance()
        return Token(TT_MOD, '%')

    def handle_lparen(self):
        self.advance()
        return Token(TT_LPAREN, '(')

    def handle_rparen(self):
        self.advance()
        return Token(TT_RPAREN, ')')

    def handle_semi(self):
        self.advance()
        return Token(TT_SEMI, ';')

    # Removed handle_colon method

    def handle_assign_or_eq(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_EQ, '==')
        return Token(TT_ASSIGN, '=')

    def handle_not_or_ne(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, '!=')
        return Token(TT_NOT, '!')

    def handle_ge(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_GE, '>=')
        self.error()

    def handle_le(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_LE, '<=')
        self.error()

    def handle_bitand(self):
        self.advance()
        return Token(TT_BITAND, '&')

    def handle_bitor(self):
        self.advance()
        return Token(TT_BITOR, '|')

    def handle_bitnot(self):
        self.advance()
        return Token(TT_BITNOT, '~')

    def handle_xor(self):
        self.advance()
        return Token(TT_XOR, '^')

    def next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            # Use op_map for operators
            if self.current_char in self.op_map:
                return self.op_map[self.current_char]()

            self.error()

        return Token(TT_EOF, None)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()
        self.variables = set()  # Track declared variables

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
            var_name = t.value
            if var_name not in self.variables:
                self.error("Variable '%s' is not defined" % var_name)
            return ('VAR', var_name)
        if t.type in [TT_MINUS, TT_NOT, TT_BITNOT]:  # Unary operators
            return ('UNARY', t.value, self.expression(UNARY_PRECEDENCE))
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
            self.consume(TT_DO)
            then_body = []
            while self.token.type not in [TT_ELSE, TT_END]:
                then_body.append(self.statement())
            if self.token.type == TT_ELSE:
                self.advance()
                # Special case for "else if"
                if self.token.type == TT_IF:
                    # Parse the if statement directly as the else branch
                    else_stmt = self.statement()
                    return ('IF', condition, then_body, [else_stmt])
                else:
                    # Regular "else do...end" block
                    self.consume(TT_DO)
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
            self.variables.add(var)  # Register variable as defined
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
            return env.get(node[1], 0)  # Default is 0 (parser ensures it exists)
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
    try:
        program = parser.parse()
        env = {}
        for node in program:
            evaluate(node, env)
        return {'success': True, 'env': env}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def should_fail(text):
    """Run code that is expected to fail and return True if it does"""
    return not run(text)['success']

def test():
    test_cases = [
        "x = 5 + 3 * 2; print x;",
        "x = 1; if x == 1 do print x; end",
        "x = 1; if x == 1 do print x; else do print 0; end",
        "x = 5 | 3; print x;",
        "x = 5 & 3; print x;",
        "x = 5 | 3; y = x & 2; print y;",
        "x = 1; y = 0; if x and y do print x; end",
        "x = 15; y = ~3; print y;",
        "x = 5 ^ 3; print x;",
        "x = -5; print x;",
        "x = 1; if x == 0 do print 0; else if x == 1 do print 1; end",
        "x = 2; if x == 0 do print 0; else if x == 1 do print 1; else do print 2; end",
        "x = 1; y = 1; z = 0; if x == 1 and y == 1 do print 1; end",
        "x = 1; y = 0; z = 1; if x == 0 or y == 1 or z == 1 do print 1; else do print 0; end",
        "x = 1; y = 1; if x == 1 and y == 0 or x == 0 and y == 1 do print 1; else do print 0; end",
        "x = 3; if x == 1 do print 1; else if x == 2 do print 2; else if x == 3 do print 3; end",
        "x = 4; if x == 1 do print 1; else if x == 2 do print 2; else if x == 3 do print 3; else do print 4; end",
        "x = 1; y = 2; if x == 1 do if y == 1 do print 1; else if y == 2 do print 2; end else do print 0; end",
        "x = 2; if x == 1 do print 1; else if x == 2 do if x == 2 do print 22; end else do print 3; end",

    ]
    
    # Test cases that are expected to fail
    fail_test_cases = [
        ("x = 1; if !x or x and y do print x; end", "Variable 'y' is not defined"),
        ("print z;", "Variable 'z' is not defined"),
        ("if x do print 1; end", "Variable 'x' is not defined")
    ]
    
    # Run test cases expected to succeed
    for i, test in enumerate(test_cases):
        print("\nTest %d:" % (i + 1))
        print("Input: %s" % test)
        result = run(test)
        if result['success']:
            print("Success! Environment: %s" % result['env'])
        else:
            print("Failed! Error: %s" % result['error'])
    
    # Run test cases expected to fail
    for i, (test, expected_error) in enumerate(fail_test_cases):
        print("\nFail Test %d:" % (i + 1))
        print("Input: %s" % test)
        result = run(test)
        if not result['success'] and expected_error in result['error']:
            print("Successfully failed with error: %s" % result['error'])
        else:
            print("Test didn't fail as expected! Result: %s" % result)

if __name__ == '__main__':
    test()
