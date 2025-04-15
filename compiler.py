# Token types
TT_EOF = 0
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
# Variable declarations
TT_VAR = 40
TT_LET = 41
# Type system additions
TT_COLON = 42
TT_TYPE_ASSIGN = 43  # :=
TT_TYPE_INT = 44
TT_TYPE_FLOAT = 45
TT_INT_LITERAL = 46
TT_FLOAT_LITERAL = 47

# Variable types
TYPE_UNKNOWN = 0
TYPE_INT = 1
TYPE_FLOAT = 2

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
    'var': TT_VAR,  # Variable declaration
    'let': TT_LET,  # Constant declaration
    'int': TT_TYPE_INT,  # Int type
    'float': TT_TYPE_FLOAT,  # Float type
}

def var_type_to_string(var_type):
    """Convert a variable type constant to a string for error messages"""
    if var_type == TYPE_INT: return "int"
    if var_type == TYPE_FLOAT: return "float"
    return "unknown"

# Global precedence table for binary operators
BINARY_PRECEDENCE = {
    TT_ASSIGN: 10,   # lowest precedence (Python: assignments)
    TT_OR: 20,       # Python: Boolean OR
    TT_AND: 30,      # Python: Boolean AND
    TT_EQ: 40,       # Python: comparisons
    TT_NE: 40,
    TT_GE: 40,
    TT_GT: 40,
    TT_LE: 40,
    TT_LT: 40,
    TT_BITOR: 50,    # Python: bitwise OR
    TT_XOR: 60,      # Python: bitwise XOR
    TT_BITAND: 70,   # Python: bitwise AND
    TT_PLUS: 80,     # Python: addition/subtraction
    TT_MINUS: 80,
    TT_MULT: 90,     # Python: multiplication/division/modulus/shift
    TT_DIV: 90,
    TT_MOD: 90,
    TT_SHL: 90,      # Python: shift has same precedence as multiplication
    TT_SHR: 90,
}

# Unary operator precedence (higher than binary operators)
UNARY_PRECEDENCE = 100

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
            ':': self.handle_colon,  # Added for type annotations
        }

    def make_token(self, token_type, value):
        """Helper to create a token with current line and column info"""
        return Token(token_type, value, self.line, self.column)

    def error(self, message="Invalid character"):
        raise Exception('%s at line %d, column %d: "%s"' %
                       (message, self.line, self.column, self.current_char))
                       
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
        """Parse a number (integer or float)"""
        start = self.pos
        
        # Track the start position for creating the token later
        start_line = self.line
        start_column = self.column
        
        # Read the first part of the number (digits before decimal point)
        while self.current_char and self.current_char.isdigit():
            self.advance()
            
        # Check for decimal point
        if self.current_char == '.':
            self.advance()
            
            # For our restricted syntax, there MUST be at least one digit after the decimal
            if not (self.current_char and self.current_char.isdigit()):
                self.error("Invalid float literal: requires digits after decimal point")
                
            # Read digits after decimal point
            while self.current_char and self.current_char.isdigit():
                self.advance()
            
            # Create a float token
            value_str = self.text[start:self.pos]
            value = float(value_str)
            return Token(TT_FLOAT_LITERAL, value, start_line, start_column)
        else:
            # Create an integer token
            value_str = self.text[start:self.pos]
            value = int(value_str)
            return Token(TT_INT_LITERAL, value, start_line, start_column)

    def identifier(self):
        """Parse an identifier or keyword using the global KEYWORDS hashtable"""
        start = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            self.advance()
        value_str = self.text[start:self.pos]

        # Look up in the global KEYWORDS hashtable, default to TT_IDENT if not found
        token_type = KEYWORDS.get(value_str, TT_IDENT)
        return self.make_token(token_type, value_str)

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
        
    def handle_colon(self):
        token = self.make_token(TT_COLON, ':')
        self.advance()
        if self.current_char == '=':
            token.type = TT_TYPE_ASSIGN
            token.value = ':='
            self.advance()
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
        self.constants = set()  # Track constants (let declarations)
        self.var_types = {}     # Track variable types
        
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

    def token_type_to_var_type(self, token_type):
        """Convert token type to variable type"""
        if token_type == TT_FLOAT_LITERAL:
            return TYPE_FLOAT
        return TYPE_INT

    def check_type_compatibility(self, var_name, expr_type):
        """Check if the expression's type is compatible with the variable's type"""
        # Get variable type
        var_type = self.var_types.get(var_name, TYPE_UNKNOWN)
        
        # Check type compatibility
        if var_type != expr_type and var_type != TYPE_UNKNOWN and expr_type != TYPE_UNKNOWN:
            self.error("Type mismatch: can't assign a value of type %s to %s (type %s)" % 
                      (var_type_to_string(expr_type), var_name, var_type_to_string(var_type)))

    def nud(self, t):
        if t.type == TT_INT_LITERAL:
            return ('NUM', t.value, TYPE_INT)
        if t.type == TT_FLOAT_LITERAL:
            return ('NUM', t.value, TYPE_FLOAT)
        if t.type == TT_IDENT:
            var_name = t.value
            # For a variable in an expression context:
            # Check if variable has been declared
            if var_name not in self.variables:
                self.error("Variable '%s' is not declared" % var_name)
                
            # Get the variable type
            var_type = self.var_types.get(var_name, TYPE_UNKNOWN)
            return ('VAR', var_name, var_type)
            
        if t.type in [TT_MINUS, TT_NOT, TT_BITNOT]:  # Unary operators
            expr = self.expression(UNARY_PRECEDENCE)
            expr_type = expr[2] if len(expr) > 2 else TYPE_INT
            return ('UNARY', t.value, expr, expr_type)
            
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
            var_type = left[2] if len(left) > 2 else TYPE_UNKNOWN
            
            # Always get the most up-to-date type from our variable table
            var_type = self.var_types.get(var_name, TYPE_UNKNOWN)
            
            # Check if variable is a constant (declared with 'let')
            if var_name in self.constants:
                self.error("Cannot reassign to constant '%s'" % var_name)
                
            # Parse the right side expression
            right = self.expression(0)
            right_type = right[2] if len(right) > 2 else TYPE_UNKNOWN
            
            # For assignments in conditions (e.g. while x = y do),
            # we should use the fully resolved types from our variable table
            if right[0] == 'VAR':
                right_var = right[1]
                right_type = self.var_types.get(right_var, right_type)
                
                # Add debug code here if needed to inspect the types
                # print("Assignment in condition: %s(%s) = %s(%s)" % 
                #      (var_name, var_type_to_string(var_type), 
                #       right_var, var_type_to_string(right_type)))
            
            # Check type compatibility
            self.check_type_compatibility(var_name, right_type)
            
            return ('ASSIGN', var_name, right, var_type)
            
        if t.type in [TT_PLUS, TT_MINUS, TT_MULT, TT_DIV, TT_MOD, TT_SHL, TT_SHR]:
            right = self.expression(self.lbp(t))
            
            # Determine result type (float if either operand is float)
            left_type = left[2] if len(left) > 2 else TYPE_INT
            right_type = right[2] if len(right) > 2 else TYPE_INT
            result_type = TYPE_FLOAT if (left_type == TYPE_FLOAT or right_type == TYPE_FLOAT) else TYPE_INT
            
            return ('BINOP', t.value, left, right, result_type)
            
        elif t.type in [TT_EQ, TT_NE, TT_GE, TT_LE, TT_LT, TT_GT]:
            right = self.expression(self.lbp(t))
            # Comparisons always return an integer (0/1 representing false/true)
            return ('COMPARE', t.value, left, right, TYPE_INT)
            
        elif t.type in [TT_AND, TT_OR]:
            right = self.expression(self.lbp(t))
            # Logical operations always return an integer (0/1 representing false/true)
            return ('LOGICAL', t.value, left, right, TYPE_INT)
            
        elif t.type in [TT_XOR, TT_BITOR, TT_BITAND]:
            right = self.expression(self.lbp(t))
            # Bit operations are performed on integers and return integers
            return ('BITOP', t.value, left, right, TYPE_INT)
            
        raise Exception('Unexpected token type %d' % t.type)

    def parse_type(self):
        """Parse a type annotation or return None if not present"""
        if self.token.type == TT_COLON:
            self.advance()  # Consume the colon
            
            # After colon, we should have a type name
            if self.token.type == TT_TYPE_INT:
                self.advance()
                return TYPE_INT
            elif self.token.type == TT_TYPE_FLOAT:
                self.advance()
                return TYPE_FLOAT
            else:
                self.error("Expected type name after ':'")
        return TYPE_UNKNOWN

    def statement(self):
        # Handle empty statements (lone semicolons)
        if self.token.type == TT_SEMI:
            self.advance()  # Skip the semicolon
            return ('EMPTY',)  # Return an empty statement node
        
        # Handle variable declarations (var and let)
        if self.token.type in [TT_VAR, TT_LET]:
            decl_type = self.token.type  # Save the declaration type (var or let)
            self.advance()
            
            # Expect an identifier after var/let
            if self.token.type != TT_IDENT:
                self.error("Expected identifier after '%s'" % ('var' if decl_type == TT_VAR else 'let'))
                
            var_name = self.token.value
            self.advance()
            
            # Process type annotation if present
            var_type = self.parse_type()  # This will consume the type if present
            
            # Check for assignment operator
            if self.token.type == TT_TYPE_ASSIGN:
                # Type inference assignment (:=)
                self.advance()  # Skip the := operator
                
                # Parse the initializer expression
                expr = self.expression(0)
                
                # Infer the type from expression
                if expr[0] == 'NUM' and len(expr) > 2:
                    var_type = expr[2]
                elif expr[0] == 'VAR':
                    # Get type from referenced variable
                    ref_var = expr[1]
                    var_type = self.var_types.get(ref_var, TYPE_UNKNOWN)
                    if var_type == TYPE_UNKNOWN:
                        self.error("Cannot infer type from variable '%s' with unknown type" % ref_var)
                elif len(expr) > 3:  # Complex expressions might have type info at the end
                    var_type = expr[-1] if isinstance(expr[-1], int) else TYPE_INT
                else:
                    # Default to int for other cases
                    var_type = TYPE_INT
                    
            elif self.token.type == TT_ASSIGN:
                # Regular assignment with explicit type (=)
                if var_type == TYPE_UNKNOWN:
                    self.error("Variable declaration with '=' requires explicit type annotation")
                    
                self.advance()  # Skip the = sign
                
                # Parse the initializer expression
                expr = self.expression(0)
                
                # Check type compatibility
                expr_type = expr[2] if len(expr) > 2 else TYPE_UNKNOWN
                if expr_type != TYPE_UNKNOWN and var_type != expr_type:
                    self.error("Type mismatch in initialization: can't assign %s to %s (type %s)" % 
                              (var_type_to_string(expr_type), var_name, var_type_to_string(var_type)))
                    
            else:
                self.error("Variable declaration must include an initialization")
            
            # Register the variable as defined
            if var_name in self.variables:
                self.error("Variable '%s' is already declared" % var_name)
                
            self.variables.add(var_name)
            self.var_types[var_name] = var_type
            
            # If this is a constant declaration (let), add it to constants set
            if decl_type == TT_LET:
                self.constants.add(var_name)
                
            self.check_statement_end()
            return ('VAR_DECL', decl_type, var_name, var_type, expr)
            
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
            
            # Check if variable has been declared
            if var not in self.variables:
                self.error("Variable '%s' is not declared" % var)
                
            # Handle all assignment operators (regular and compound)
            if self.token.type in [TT_ASSIGN, TT_PLUS_ASSIGN, TT_MINUS_ASSIGN, 
                                  TT_MULT_ASSIGN, TT_DIV_ASSIGN, TT_MOD_ASSIGN]:
                # Check if variable is a constant (declared with 'let')
                if var in self.constants:
                    self.error("Cannot reassign to constant '%s'" % var)
                    
                op = self.token.type
                op_value = self.token.value
                var_type = self.var_types.get(var, TYPE_UNKNOWN)
                
                # Advance past the operator
                self.advance()
                
                # Parse the expression
                expr = self.expression(0)
                expr_type = expr[2] if len(expr) > 2 else TYPE_UNKNOWN
                
                # We need to handle the case where the compiler doesn't have an updated
                # type for the variable in the AST yet, so get the type from our type tracking
                var_type = self.var_types.get(var, TYPE_UNKNOWN)
                
                # Check type compatibility for all assignments
                self.check_type_compatibility(var, expr_type)
                
                # For compound operators, we need to generate ("COMPOUND_ASSIGN", op_type, var, expr)
                if op != TT_ASSIGN:
                    self.check_statement_end()
                    return ('COMPOUND_ASSIGN', op, var, expr, var_type)
                    
                # Regular assignment
                self.check_statement_end()
                return ('ASSIGN', var, expr, var_type)
            # Handle expression statements (e.g., an identifier by itself)
            var_type = self.var_types.get(var, TYPE_UNKNOWN)
            expr = ('VAR', var, var_type)
            self.check_statement_end()
            return ('EXPR_STMT', expr)
        elif self.token.type in [TT_INT_LITERAL, TT_FLOAT_LITERAL, TT_LPAREN, TT_MINUS, TT_NOT, TT_BITNOT]:
            # Also handle expressions that start with other tokens
            expr = self.expression(0)
            self.check_statement_end()
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
            return node[1]  # The value is at index 1, type at index 2
        elif node[0] == 'VAR':
            return env.get(node[1], 0)  # Default is 0 (parser ensures it exists)
        elif node[0] == 'BREAK':
            raise BreakException()
        elif node[0] == 'CONTINUE':
            raise ContinueException()
        elif node[0] == 'VAR_DECL':
            # Variable declaration node: ('VAR_DECL', decl_type, var_name, var_type, expr)
            var_name = node[2]
            value = evaluate(node[4], env)
            env[var_name] = value
            return value
        elif node[0] == 'BINOP':
            left = evaluate(node[2], env)  # The left operand
            right = evaluate(node[3], env)  # The right operand
            op = node[1]
            result_type = node[4] if len(node) > 4 else TYPE_INT  # Get result type if available
            
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': 
                # Handle division based on result type
                if result_type == TYPE_INT and isinstance(left, int) and isinstance(right, int):
                    return left // right  # Integer division
                else:
                    return left / right  # Float division
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
                # Handle division based on operand types
                var_type = node[4] if len(node) > 4 else TYPE_UNKNOWN
                if var_type == TYPE_INT and isinstance(current_value, int) and isinstance(expr_value, int):
                    result = current_value // expr_value  # Integer division
                else:
                    result = current_value / expr_value  # Float division
            elif op_type == TT_MOD_ASSIGN:
                result = current_value % expr_value
            else:
                # This should never happen if parser is correct
                raise Exception("Unknown compound assignment operator: %s" % token_name(op_type))
                
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

# Define token type names for debugging
TOKEN_NAMES = {v: k for k, v in globals().items() if k.startswith('TT_')}

def token_name(token_type):
    """Convert a token type number to its name for better debugging"""
    return TOKEN_NAMES.get(token_type, str(token_type))
