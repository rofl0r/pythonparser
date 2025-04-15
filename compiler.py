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
TT_WHILE = 28
TT_LT = 29
TT_GT = 30
TT_BREAK = 31
TT_CONTINUE = 32
# Compound assignment operators
TT_PLUS_ASSIGN = 33
TT_MINUS_ASSIGN = 34
TT_MULT_ASSIGN = 35
TT_DIV_ASSIGN = 36
TT_MOD_ASSIGN = 37
TT_SHR = 38
TT_SHL = 39

# Global hashtable for keywords
KEYWORDS = {
    'if': TT_IF,
    'else': TT_ELSE,
    'end': TT_END,
    'print': TT_PRINT,
    'and': TT_AND,
    'or': TT_OR,
    'do': TT_DO,
    'while': TT_WHILE,
    'break': TT_BREAK,
    'continue': TT_CONTINUE,
    'xor': TT_XOR,
    'bitnot': TT_BITNOT,
    'shl': TT_SHL,
    'shr': TT_SHR,
}

# Global precedence table for binary operators
BINARY_PRECEDENCE = {
    TT_ASSIGN: 5, # lowest precedence
    TT_OR: 10,
    TT_AND: 20,
    TT_BITOR: 30,
    TT_XOR: 40,
    TT_BITAND: 50,
    TT_EQ: 60,
    TT_NE: 60,
    TT_GE: 60,
    TT_GT: 60,
    TT_LE: 60,
    TT_LT: 60,
    TT_PLUS: 70,
    TT_MINUS: 70,
    TT_SHL: 75,
    TT_SHR: 75,
    TT_MULT: 80,
    TT_DIV: 80,
    TT_MOD: 80,
}

# Unary operator precedence (higher than binary operators)
UNARY_PRECEDENCE = 90

class Token:
    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return 'Token(%d, %s)' % (self.type, self.value)

class Lexer:
    def __init__(self, text):
        self.text = text
        self.line = 1      # Current line number (1-based)
        self.column = 1    # Current column number (1-based)
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
            '=': self.handle_assign_or_eq,
            '!': self.handle_not_or_ne,
            '>': self.handle_ge,
            '<': self.handle_le,
            '&': self.handle_bitand,
            '|': self.handle_bitor,
        }

    def make_token(self, token_type, value):
        """Helper to create a token with current line and column info"""
        return Token(token_type, value, self.line, self.column)

    def error(self):
        raise Exception('Invalid character at line %d, column %d: "%s"' %
                       (self.line, self.column, self.current_char))
    def advance(self):
        # Update line and column tracking
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        start = self.pos
        while self.current_char and self.current_char.isdigit():
            self.advance()
        return self.make_token(TT_NUMBER, int(self.text[start:self.pos]))

    def identifier(self):
        """Parse an identifier or keyword using the global KEYWORDS hashtable"""
        start = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            self.advance()
        value = self.text[start:self.pos]

        # Look up in the global KEYWORDS hashtable, default to TT_IDENT if not found
        token_type = KEYWORDS.get(value, TT_IDENT)
        return self.make_token(token_type, value)

    # Handlers for various operators
    def handle_plus(self):
        token = self.make_token(TT_PLUS, '+')
        self.advance()
        if self.current_char == '=':
            token.type = TT_PLUS_ASSIGN
            token.value = '+='
            self.advance()
        return token

    def handle_minus(self):
        token = self.make_token(TT_MINUS, '-')
        self.advance()
        if self.current_char == '=':
            token.type = TT_MINUS_ASSIGN
            token.value = '-='
            self.advance()
        return token

    def handle_mult(self):
        token = self.make_token(TT_MULT, '*')
        self.advance()
        if self.current_char == '=':
            token.type = TT_MULT_ASSIGN
            token.value = '*='
            self.advance()
        return token

    def handle_div(self):
        token = self.make_token(TT_DIV, '/')
        self.advance()
        if self.current_char == '=':
            token.type = TT_DIV_ASSIGN
            token.value = '/='
            self.advance()
        return token

    def handle_mod(self):
        token = self.make_token(TT_MOD, '%')
        self.advance()
        if self.current_char == '=':
            token.type = TT_MOD_ASSIGN
            token.value = '%='
            self.advance()
        return token

    def handle_lparen(self):
        token = self.make_token(TT_LPAREN, '(')
        self.advance()
        return token

    def handle_rparen(self):
        token = self.make_token(TT_RPAREN, ')')
        self.advance()
        return token

    def handle_semi(self):
        token = self.make_token(TT_SEMI, ';')
        self.advance()
        return token

    def handle_assign_or_eq(self):
        token = self.make_token(TT_ASSIGN, '=')
        self.advance()
        if self.current_char == '=':
            token.type = TT_EQ
            token.value = '=='
            self.advance()
        return token

    def handle_not_or_ne(self):
        token = self.make_token(TT_NOT, '!')
        self.advance()
        if self.current_char == '=':
            token.type = TT_NE
            token.value = '!='
            self.advance()
        return token

    def handle_ge(self):
        token = self.make_token(TT_GT, '>')
        self.advance()
        if self.current_char == '=':
            token.type = TT_GE
            token.value = '>='
            self.advance()
        return token

    def handle_le(self):
        token = self.make_token(TT_LT, '<')
        self.advance()
        if self.current_char == '=':
            token.type = TT_LE
            token.value = '<='
            self.advance()
        return token

    def handle_bitand(self):
        token = self.make_token(TT_BITAND, '&')
        self.advance()
        # No &= operator since we use keywords for bitwise operations
        return token

    def handle_bitor(self):
        token = self.make_token(TT_BITOR, '|')
        self.advance()
        # No |= operator since we use keywords for bitwise operations
        return token

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

        return self.make_token(TT_EOF, None)

# Custom exceptions for control flow
class BreakException(Exception):
    """Raised when a break statement is encountered"""
    pass
    
class ContinueException(Exception):
    """Raised when a continue statement is encountered"""
    pass

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token() # Current token
        self.prev_token = None  # Previous token (for better error messages)
        self.variables = set()  # Track declared variables

    def error(self, message):
        token_type_name = token_name(self.token.type)
        raise Exception("%s at line %d, column %d. Token: %s (%s)" %
                       (message, self.lexer.line, self.lexer.column,
                        self.token.value, token_type_name))

    def advance(self):
        self.prev_token = self.token
        self.token = self.lexer.next_token()

    def consume(self, token_type):
        if self.token.type == token_type:
            self.advance()
        else:
            expected_type_name = token_name(token_type)
            actual_type_name = token_name(self.token.type)
            self.error('Expected %s but got %s' %
                       (expected_type_name, actual_type_name))
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
            # For a variable in an expression context:
            # 1. If it's already registered, we can use its value
            # 2. If not, we'll register it now - it might be the left side of an assignment
            if var_name not in self.variables and self.token.type != TT_ASSIGN:
                # Only error if we're not about to see an assignment
                self.error("Variable '%s' is not defined" % var_name)
            self.variables.add(var_name)  # Register variable
            return ('VAR', var_name)
        if t.type in [TT_MINUS, TT_NOT, TT_BITNOT]:  # Unary operators
            return ('UNARY', t.value, self.expression(UNARY_PRECEDENCE))
        if t.type == TT_LPAREN:
            expr = self.expression(0)
            self.consume(TT_RPAREN)
            return expr
        raise Exception('Unexpected token type %d' % t.type)

    def led(self, t, left):
        # Handle assignment as an operator
        if t.type == TT_ASSIGN and left[0] == 'VAR':
            # Get variable name from left side
            var_name = left[1]
            # Parse the right side expression
            right = self.expression(0)
            return ('ASSIGN', var_name, right)
        if t.type in [TT_PLUS, TT_MINUS, TT_MULT, TT_DIV, TT_MOD, TT_SHL, TT_SHR]:
            return ('BINOP', t.value, left, self.expression(self.lbp(t)))
        elif t.type in [TT_EQ, TT_NE, TT_GE, TT_LE, TT_LT, TT_GT]:
            return ('COMPARE', t.value, left, self.expression(self.lbp(t)))
        elif t.type in [TT_AND, TT_OR]:
            return ('LOGICAL', t.value, left, self.expression(self.lbp(t)))
        elif t.type in [TT_XOR, TT_BITOR, TT_BITAND]:
            return ('BITOP', t.value, left, self.expression(self.lbp(t)))
        raise Exception('Unexpected token type %d' % t.type)

    def statement(self):
        # Handle empty statements (lone semicolons)
        if self.token.type == TT_SEMI:
            self.advance()  # Skip the semicolon
            return ('EMPTY',)  # Return an empty statement node
            
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
        elif self.token.type == TT_WHILE:
            self.advance()
            condition = self.expression(0)
            self.consume(TT_DO)
            body = []
            while self.token.type != TT_END:
                body.append(self.statement())
            self.consume(TT_END)
            return ('WHILE', condition, body)
        elif self.token.type == TT_PRINT:
            self.advance()
            expr = self.expression(0)
            self.check_statement_end()
            return ('PRINT', expr)
        elif self.token.type == TT_BREAK:
            self.advance()
            self.check_statement_end()
            return ('BREAK',)
        elif self.token.type == TT_CONTINUE:
            self.advance()
            self.check_statement_end()
            return ('CONTINUE',)
        elif self.token.type == TT_IDENT:
            var = self.token.value
            self.advance()
            self.variables.add(var)  # Register variable as defined
            
            # Handle all assignment operators (regular and compound)
            if self.token.type in [TT_ASSIGN, TT_PLUS_ASSIGN, TT_MINUS_ASSIGN, 
                                  TT_MULT_ASSIGN, TT_DIV_ASSIGN, TT_MOD_ASSIGN]:
                op = self.token.type
                op_value = self.token.value
                self.advance()
                expr = self.expression(0) 
                
                # For compound operators, we need to generate ("COMPOUND_ASSIGN", op_type, var, expr)
                if op != TT_ASSIGN:
                    self.check_statement_end("do")
                    return ('COMPOUND_ASSIGN', op, var, expr)
                    
                # Regular assignment
                self.check_statement_end("do")
                return ('ASSIGN', var, expr)
            # Handle expression statements (e.g., an identifier by itself)
            expr = ('VAR', var)
            self.check_statement_end()
            return ('EXPR_STMT', expr)
        elif self.token.type in [TT_NUMBER, TT_LPAREN, TT_MINUS, TT_NOT, TT_BITNOT]:
            # Also handle expressions that start with other tokens
            expr = self.expression(0)
            self.check_statement_end("do")
            return ('EXPR_STMT', expr)
        token_type_name = token_name(self.token.type)
        self.error('Invalid statement starting with "%s" (%s)' %
                  (self.token.value, token_type_name))
                  
    def check_statement_end(self, allow_also=None):
        """Check if a statement is properly terminated by semicolon, newline, or EOF"""
        # Allow specific token (e.g. "do" for assignments in if/while conditions)
        if allow_also and self.token.type == globals().get('TT_' + allow_also.upper(), 0):
            return
        
        # Consume semicolon if present
        if self.token.type == TT_SEMI:
            self.advance()
            return
            
        # Check if we're at the end of a line or file
        if self.token.type != TT_EOF and self.prev_token and self.token.line == self.prev_token.line:
            self.error("Expected semicolon between statements on the same line")

    def parse(self):
        statements = []
        while self.token.type != TT_EOF:
            statements.append(self.statement())
        return statements

def evaluate(node, env):
    if isinstance(node, tuple):
        # Handle empty statements (do nothing)
        if node[0] == 'EMPTY':
            return 0
        if node[0] == 'NUM':
            return node[1]
        elif node[0] == 'VAR':
            return env.get(node[1], 0)  # Default is 0 (parser ensures it exists)
        elif node[0] == 'BREAK':
            raise BreakException()
        elif node[0] == 'CONTINUE':
            raise ContinueException()
        elif node[0] == 'BINOP':
            left = evaluate(node[2], env)
            right = evaluate(node[3], env)
            op = node[1]
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': return left // right if isinstance(left, int) else left / right  # Python 2 compatibility
            elif op == '%': return left % right
            elif op == 'shl': return left << right
            elif op == 'shr': return left >> right

        elif node[0] == 'UNARY':
            right = evaluate(node[2], env)
            op = node[1]
            if op == '-': return -right
            elif op == '!': return 0 if right else 1
            elif op == 'bitnot': return ~right
        elif node[0] == 'ASSIGN':
            value = evaluate(node[2], env)
            env[node[1]] = value
            return value
        elif node[0] == 'COMPOUND_ASSIGN':
            op_type = node[1]
            var = node[2]
            expr_value = evaluate(node[3], env)
            
            # Get the current value of the variable (defaulting to 0 if not set)
            current_value = env.get(var, 0)
            
            # Perform the appropriate operation based on the operator type
            if op_type == TT_PLUS_ASSIGN:
                result = current_value + expr_value
            elif op_type == TT_MINUS_ASSIGN:
                result = current_value - expr_value
            elif op_type == TT_MULT_ASSIGN:
                result = current_value * expr_value
            elif op_type == TT_DIV_ASSIGN:
                # Handle integer division
                result = current_value // expr_value if isinstance(current_value, int) else current_value / expr_value
            elif op_type == TT_MOD_ASSIGN:
                result = current_value % expr_value
            else:
                # This should never happen if parser is correct
                raise Exception("Unknown compound assignment operator: %s"%token_name(op_type))
                
            # Store the result back in the variable and return it
            env[var] = result
            return result
        elif node[0] == 'EXPR_STMT':
            # Evaluate the expression and discard the result
            # (For expressions used as statements)
            return evaluate(node[1], env)
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
        elif node[0] == 'WHILE':
            while evaluate(node[1], env):  # Evaluate condition
                try:
                    for stmt in node[2]:  # Execute body
                        try:
                            evaluate(stmt, env)
                        except ContinueException:
                            # Skip rest of current iteration
                            break
                        except BreakException:
                            # Exit the loop completely
                            raise
                except BreakException:
                    # Exit the loop
                    break
            return 0
        elif node[0] == 'COMPARE':
            left = evaluate(node[2], env)
            right = evaluate(node[3], env)
            op = node[1]
            if op == '==': return 1 if left == right else 0
            elif op == '!=': return 1 if left != right else 0
            elif op == '>=': return 1 if left >= right else 0
            elif op == '>': return 1 if left > right else 0
            elif op == '<': return 1 if left < right else 0
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
            elif op == 'xor': return left ^ right
    return 0

def run(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    try:
        program = parser.parse()
        env = {}
        ast = program
        for node in program:
            evaluate(node, env)
        return {'success': True, 'env': env, 'ast': ast}
    except Exception as e:
        return {'success': False, 'error': str(e), 'ast': None}

def should_fail(text):
    """Run code that is expected to fail and return True if it does"""
    return not run(text)['success']

def test():
    # Test cases with expected final env state
    test_cases = [
        {
            "code": "x = 0; y = 0; while x = y do y = y + 1; end; print x;",
            "expected_env": {"x": 0, "y": 0}
        },
        {
            "code": "x = 5 + 3 * 2; print x;",
            "expected_env": {"x": 11}
        },
        {
            "code": "x = 1; if x == 1 do print x; end", 
            "expected_env": {"x": 1}
        },
        {
            "code": "x = 1; if x == 1 do print x; else do print 0; end",
            "expected_env": {"x": 1}
        },
        {
            "code": "x = 5 | 3; print x;", 
            "expected_env": {"x": 7}
        },
        {
            "code": "x = 5 & 3; print x;", 
            "expected_env": {"x": 1}
        },
        {
            "code": "x = 5 | 3; y = x & 2; print y;",
            "expected_env": {"x": 7, "y": 2}
        },
        {
            "code": "x = 1; y = 0; if x and y do print x; end", 
            "expected_env": {"x": 1, "y": 0}
        },
        {
            "code": "x = 5 xor 3; print x;",
            "expected_env": {"x": 6}  # 5 xor 3 = 6
        },
        {
            "code": "x = 7; y = x xor 2; print y;",
            "expected_env": {"x": 7, "y": 5}  # 7 xor 2 = 5
        },
        {
            "code": "x = 15; y = bitnot 3; print y;", 
            "expected_env": {"x": 15, "y": -4}
        },
        {
            "code": "x = 1; if x == 0 do print 0; else if x == 1 do print 1; end",
            "expected_env": {"x": 1}
        },
        {
            "code": "x = 3; if x == 1 do print 1; else if x == 2 do print 2; else if x == 3 do print 3; end",
            "expected_env": {"x": 3}
        },
        {
            "code": "x = 2; if x == 1 do print 1; else if x == 2 do if x == 2 do print 22; end else do print 3; end",
            "expected_env": {"x": 2}
        },
        # While loop test cases
        {
            "code": "x = 0; while x < 5 do x = x + 1; end print x;",
            "expected_env": {"x": 5}
        },
        {
            "code": "x = 0; y = 0; while x < 3 do y = y + x; x = x + 1; end",
            "expected_env": {"x": 3, "y": 3}  # y = 0+0 + 0+1 + 1+2 = 3
        },
        {
            "code": "x = 10; while x > 0 do x = x - 2; end",
            "expected_env": {"x": 0}
        },
        {
            "code": "x = 1; y = 1; while x < 10 do x = x * 2; y = y + x; end",
            "expected_env": {"x": 16, "y": 31}  # y = 1+2 + 2+4 + 6+8 + 14+16 = 31
        },
        # Break statement tests
        {
            "code": "x = 0; while x < 10 do x = x + 1; if x == 5 do break; end end",
            "expected_env": {"x": 5}
        },
        {
            "code": "sum = 0; x = 0; while x < 10 do x = x + 1; if x > 5 do break; end sum = sum + x; end",
            "expected_env": {"sum": 15, "x": 6}  # sum = 1+2+3+4+5 = 15
        },
        # Continue statement tests
        {
            "code": "sum = 0; x = 0; while x < 5 do x = x + 1; if x == 3 do continue; end sum = sum + x; end",
            "expected_env": {"sum": 12, "x": 5}  # sum = 1+2+4+5 = 12 (3 is skipped)
        },
        {
            "code": "evens = 0; x = 0; while x < 10 do x = x + 1; if x % 2 != 0 do continue; end evens = evens + x; end",
            "expected_env": {"evens": 30, "x": 10}  # evens = 2+4+6+8+10 = 30
        },
        {
            "code": "x = 0; sum = 0; while x < 10 do x = x + 1; if x < 5 do continue; end if x > 8 do break; end sum = sum + x; end",
            "expected_env": {"x": 9, "sum": 26}  # sum = 5+6+7+8 = 26
        },
        {
            "code": "x = 5;;; y = 10;;;",  # Test multiple semicolons
            "expected_env": {"x": 5, "y": 10}
        },
        {
            "code": "x = 5\ny = 10\nz = x + y",  # Test newlines instead of semicolons
            "expected_env": {"x": 5, "y": 10, "z": 15}
        },
        {
            "code": "x = 1; y = 2; z = 3;",  # Mix of with/without semicolons
            "expected_env": {"x": 1, "y": 2, "z": 3}
        },
        {
            "code": "a = 1;\nb = 2\nc = 3",  # New lines instead of semicolons
            "expected_env": {"a": 1, "b": 2, "c": 3}
        },
        {
            "code": "a = 1; b = 2; c = 3",  # Semicolons on the same line - should work
            "expected_env": {"a": 1, "b": 2, "c": 3}
        },
        {
            "code": "x = 5 + 3\nprint x",  # Missing semicolon but on different lines - should work
            "expected_env": {"x": 8}
        },
        # Compound assignment operators tests
        {
            "code": "x = 5; x += 3; print x;",
            "expected_env": {"x": 8}
        },
        {
            "code": "x = 10; x -= 4; print x;",
            "expected_env": {"x": 6}
        },
        {
            "code": "x = 3; x *= 5; print x;",
            "expected_env": {"x": 15}
        },
        {
            "code": "x = 20; x /= 4; print x;",
            "expected_env": {"x": 5}
        },
        {
            "code": "x = 17; x %= 5; print x;",
            "expected_env": {"x": 2}
        },
        {
            "code": "x = 1; y = 2; x += y; y *= 3; print x; print y;", 
            "expected_env": {"x": 3, "y": 6}
        },
        {
            "code": "x = 5; y = x shl 2; print y;", # 5 << 2 = 20
            "expected_env": {"x": 5, "y": 20}
        },
        {
            "code": "x = 20; y = x shr 2; print y;", # 20 >> 2 = 5
            "expected_env": {"x": 20, "y": 5}
        },
    ]
    
    # Test cases that are expected to fail
    fail_test_cases = [
        {
            "code": "x = 1; if !x or x and y do print x; end",
            "expected_error": "Variable 'y' is not defined"
        },
        {
            "code": "print z;",
            "expected_error": "Variable 'z' is not defined"
        },
        {
            "code": "if x do print 1; end",
            "expected_error": "Variable 'x' is not defined" 
        },
        {
            "code": "x = 5 + 3 print x;",  # Missing semicolon between statements on the same line
            "expected_error": "Expected semicolon between statements"
        },
        {
            "code": "a = 1 b = 2",  # No semicolon between statements on the same line
            "expected_error": "Expected semicolon between statements"
        }
    ]
    
    # Run test cases expected to succeed
    for i, test_case in enumerate(test_cases):
        print("\nTest %d:" % (i + 1))
        print("Input: %s" % test_case["code"])
        result = run(test_case["code"])
        if result['success']:
            # Check if environment values match
            env_match = True
            for k, v in test_case["expected_env"].items():
                if k not in result['env'] or result['env'][k] != v:
                    env_match = False
                    break
            
            if env_match:
                print("Success! Environment matches expectations.")
            else:
                print("Test passed but with incorrect environment values:")
                print("  Expected env: %s" % test_case["expected_env"])
                print("  Actual env: %s" % result['env'])
        else:
            print("Failed! Error: %s" % result['error'])
            if result.get('ast'):
                print("AST dump: %s" % result['ast'])

    # Run test cases expected to fail
    for i, test_case in enumerate(fail_test_cases):
        print("\nFail Test %d:" % (i + 1))
        print("Input: %s" % test_case["code"])
        result = run(test_case["code"])
        if not result['success'] and test_case["expected_error"] in result['error']:
            print("Successfully failed with error: %s" % result['error'])
        else:
            print("Test didn't fail as expected! Result: %s" % result)
            # Add AST dump for unexpected failures
            if result.get('ast'):
                print("AST dump: %s" % result['ast'])

# Define token type names for debugging
TOKEN_NAMES = {v: k for k, v in globals().items() if k.startswith('TT_')}

def token_name(token_type):
    """Convert a token type number to its name for better debugging"""
    return TOKEN_NAMES.get(token_type, str(token_type))

if __name__ == '__main__':
    test()
