# Implementation of a Pratt parser in Python 2.7
from interpreter import *
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
TT_SHL = 38
TT_SHR = 39
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
TT_TYPE_UINT = 48
TT_TYPE_LONG = 49
TT_TYPE_ULONG = 50
TT_UINT_LITERAL = 51
TT_LONG_LITERAL = 52
TT_ULONG_LITERAL = 53

# AST Node types (C-style enums)
AST_NODE_BASE = 0
AST_NODE_NUMBER = 1
AST_NODE_VARIABLE = 2
AST_NODE_BINARY_OP = 3
AST_NODE_UNARY_OP = 4
AST_NODE_ASSIGN = 5
AST_NODE_COMPOUND_ASSIGN = 6
AST_NODE_PRINT = 7
AST_NODE_IF = 8
AST_NODE_WHILE = 9
AST_NODE_BREAK = 10
AST_NODE_CONTINUE = 11
AST_NODE_EXPR_STMT = 12
AST_NODE_VAR_DECL = 13
AST_NODE_EMPTY = 14
AST_NODE_COMPARE = 15
AST_NODE_LOGICAL = 16
AST_NODE_BITOP = 17

# Variable types
TYPE_UNKNOWN = 0
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_UINT = 3
TYPE_LONG = 4
TYPE_ULONG = 5

# Order of type precedence (highest to lowest)
TYPE_PRECEDENCE = [TYPE_FLOAT, TYPE_ULONG, TYPE_LONG, TYPE_UINT, TYPE_INT]

# Mapping from type constants to their string representations
TYPE_TO_STRING_MAP = {
    TYPE_UNKNOWN: "unknown",
    TYPE_INT: "int",
    TYPE_FLOAT: "float",
    TYPE_UINT: "uint",
    TYPE_LONG: "long",
    TYPE_ULONG: "ulong"
}

# Mapping from token types to variable types
TOKEN_TO_TYPE_MAP = {
    TT_INT_LITERAL: TYPE_INT,
    TT_FLOAT_LITERAL: TYPE_FLOAT,
    TT_UINT_LITERAL: TYPE_UINT,
    TT_LONG_LITERAL: TYPE_LONG,
    TT_ULONG_LITERAL: TYPE_ULONG
}

# Mapping from type tokens to variable types
TYPE_TOKEN_MAP = {
    TT_TYPE_INT: TYPE_INT,
    TT_TYPE_FLOAT: TYPE_FLOAT,
    TT_TYPE_UINT: TYPE_UINT,
    TT_TYPE_LONG: TYPE_LONG,
    TT_TYPE_ULONG: TYPE_ULONG
}

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
    'uint': TT_TYPE_UINT,  # Unsigned Int type
    'long': TT_TYPE_LONG,  # Long type
    'ulong': TT_TYPE_ULONG,  # Unsigned Long type
}

def var_type_to_string(var_type):
    """Convert a variable type constant to a string for error messages using the map"""
    return TYPE_TO_STRING_MAP.get(var_type, "unknown")

def ast_node_type_to_string(node_type):
    """Convert AST node type to string for debugging"""
    type_names = {
        AST_NODE_BASE: "BASE",
        AST_NODE_NUMBER: "NUMBER",
        AST_NODE_VARIABLE: "VARIABLE",
        AST_NODE_BINARY_OP: "BINARY_OP",
        AST_NODE_UNARY_OP: "UNARY_OP",
        AST_NODE_ASSIGN: "ASSIGN",
        AST_NODE_COMPOUND_ASSIGN: "COMPOUND_ASSIGN",
        AST_NODE_PRINT: "PRINT",
        AST_NODE_IF: "IF",
        AST_NODE_WHILE: "WHILE",
        AST_NODE_BREAK: "BREAK",
        AST_NODE_CONTINUE: "CONTINUE",
        AST_NODE_EXPR_STMT: "EXPR_STMT",
        AST_NODE_VAR_DECL: "VAR_DECL",
        AST_NODE_EMPTY: "EMPTY",
        AST_NODE_COMPARE: "COMPARE",
        AST_NODE_LOGICAL: "LOGICAL",
        AST_NODE_BITOP: "BITOP"
    }
    return type_names.get(node_type, "UNKNOWN")

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

# Base class for all AST nodes
class ASTNode(object):
    def __init__(self, node_type=AST_NODE_BASE):
        self.node_type = node_type

    def eval(self, env):
        raise NotImplementedError("Evaluation not implemented for this node")

class NumberNode(ASTNode):
    def __init__(self, value, expr_type):
        ASTNode.__init__(self, AST_NODE_NUMBER)
        self.value = value
        self.expr_type = expr_type  # TYPE_INT, TYPE_FLOAT, TYPE_UINT, TYPE_LONG, TYPE_ULONG

    def eval(self, env):
        return self.value

class VariableNode(ASTNode):
    def __init__(self, name, var_type):
        ASTNode.__init__(self, AST_NODE_VARIABLE)
        self.name = name
        self.expr_type = var_type

    def eval(self, env):
        if self.name not in env:
            raise RuntimeError("Variable '%s' is not defined" % self.name)
        return env[self.name]

class BinaryOpNode(ASTNode):
    def __init__(self, operator, left, right, result_type):
        ASTNode.__init__(self, AST_NODE_BINARY_OP)
        self.operator = operator
        self.left = left
        self.right = right
        self.expr_type = result_type

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        
        if self.operator == '+':
            return add(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '-':
            return subtract(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '*':
            return multiply(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '/':
            return divide(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '%':
            return modulo(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == 'shl':
            return shift_left(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == 'shr':
            return shift_right(left_val, right_val, self.left.expr_type, self.right.expr_type)

class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand, result_type):
        ASTNode.__init__(self, AST_NODE_UNARY_OP)
        self.operator = operator
        self.operand = operand
        self.expr_type = result_type

    def eval(self, env):
        value = self.operand.eval(env)
        
        if self.operator == '-':
            return negate(value, self.operand.expr_type)
        elif self.operator == '!':
            return logical_not(value)
        elif self.operator == 'bitnot':
            return bitwise_not(value, self.operand.expr_type)

class AssignNode(ASTNode):
    def __init__(self, var_name, expr, var_type):
        ASTNode.__init__(self, AST_NODE_ASSIGN)
        self.var_name = var_name
        self.expr = expr
        self.expr_type = var_type

    def eval(self, env):
        value = self.expr.eval(env)
        env[self.var_name] = value
        return value

class CompoundAssignNode(ASTNode):
    def __init__(self, op_type, var_name, expr, var_type):
        ASTNode.__init__(self, AST_NODE_COMPOUND_ASSIGN)
        self.op_type = op_type
        self.var_name = var_name
        self.expr = expr
        self.expr_type = var_type

    def eval(self, env):
        current_value = env.get(self.var_name, 0)
        expr_value = self.expr.eval(env)
        
        if self.op_type == TT_PLUS_ASSIGN:
            result = add(current_value, expr_value, self.expr_type, self.expr.expr_type)
        elif self.op_type == TT_MINUS_ASSIGN:
            result = subtract(current_value, expr_value, self.expr_type, self.expr.expr_type)
        elif self.op_type == TT_MULT_ASSIGN:
            result = multiply(current_value, expr_value, self.expr_type, self.expr.expr_type)
        elif self.op_type == TT_DIV_ASSIGN:
            result = divide(current_value, expr_value, self.expr_type, self.expr.expr_type)
        elif self.op_type == TT_MOD_ASSIGN:
            result = modulo(current_value, expr_value, self.expr_type, self.expr.expr_type)
            
            
        env[self.var_name] = result
        return result

class PrintNode(ASTNode):
    def __init__(self, expr):
        ASTNode.__init__(self, AST_NODE_PRINT)
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        print(value)
        return value

class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        ASTNode.__init__(self, AST_NODE_IF)
        self.condition = condition
        self.then_body = then_body  # List of statement nodes
        self.else_body = else_body  # List of statement nodes or None

    def eval(self, env):
        if self.condition.eval(env):
            for stmt in self.then_body:
                stmt.eval(env)
        elif self.else_body:
            for stmt in self.else_body:
                stmt.eval(env)
        return 0

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        ASTNode.__init__(self, AST_NODE_WHILE)
        self.condition = condition
        self.body = body  # List of statement nodes

    def eval(self, env):
        while self.condition.eval(env):
            try:
                for stmt in self.body:
                    try:
                        stmt.eval(env)
                    except ContinueException:
                        break
                    except BreakException:
                        raise
            except BreakException:
                break
        return 0

class BreakNode(ASTNode):
    def __init__(self):
        ASTNode.__init__(self, AST_NODE_BREAK)

    def eval(self, env):
        raise BreakException()

class ContinueNode(ASTNode):
    def __init__(self):
        ASTNode.__init__(self, AST_NODE_CONTINUE)

    def eval(self, env):
        raise ContinueException()

class ExprStmtNode(ASTNode):
    def __init__(self, expr):
        ASTNode.__init__(self, AST_NODE_EXPR_STMT)
        self.expr = expr

    def eval(self, env):
        return self.expr.eval(env)

class VarDeclNode(ASTNode):
    def __init__(self, decl_type, var_name, var_type, expr):
        ASTNode.__init__(self, AST_NODE_VAR_DECL)
        self.decl_type = decl_type
        self.var_name = var_name
        self.var_type = var_type
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        env[self.var_name] = value
        return value

class EmptyNode(ASTNode):
    def __init__(self):
        ASTNode.__init__(self, AST_NODE_EMPTY)

    def eval(self, env):
        return 0

class CompareNode(ASTNode):
    def __init__(self, operator, left, right):
        ASTNode.__init__(self, AST_NODE_COMPARE)
        self.operator = operator
        self.left = left
        self.right = right
        self.expr_type = TYPE_INT  # Comparisons always return int

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        
        if self.operator == '==':
            return compare_eq(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '!=':
            return compare_ne(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '>=':
            return compare_ge(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '>':
            return compare_gt(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '<':
            return compare_lt(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '<=':
            return compare_le(left_val, right_val, self.left.expr_type, self.right.expr_type)

class LogicalNode(ASTNode):
    def __init__(self, operator, left, right):
        ASTNode.__init__(self, AST_NODE_LOGICAL)
        self.operator = operator
        self.left = left
        self.right = right
        self.expr_type = TYPE_INT  # Logical ops always return int

    def eval(self, env):
        left_val = self.left.eval(env)
        
        if self.operator == 'and':
            return logical_and(left_val, self.right.eval(env))
        elif self.operator == 'or':
            return logical_or(left_val, self.right.eval(env))

class BitOpNode(ASTNode):
    def __init__(self, operator, left, right):
        ASTNode.__init__(self, AST_NODE_BITOP)
        self.operator = operator
        self.left = left
        self.right = right
        self.expr_type = TYPE_INT  # Bitwise ops always return int

    def eval(self, env):
        left_val = self.left.eval(env)
        right_val = self.right.eval(env)
        
        if self.operator == '&':
            return bitwise_and(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == '|':
            return bitwise_or(left_val, right_val, self.left.expr_type, self.right.expr_type)
        elif self.operator == 'xor':
            return bitwise_xor(left_val, right_val, self.left.expr_type, self.right.expr_type)

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

        # Check for suffix first (u, l, ul, lu) - needs to be checked before decimal point
        if self.current_char in ['u', 'U', 'l', 'L']:
            num_value = int(self.text[start:self.pos])
            suffix = self.parse_int_suffix()
            
            # Create appropriate token based on suffix
            if suffix == 'u': return Token(TT_UINT_LITERAL, num_value, start_line, start_column)
            if suffix == 'l': return Token(TT_LONG_LITERAL, num_value, start_line, start_column)
            if suffix in ['ul', 'lu']: return Token(TT_ULONG_LITERAL, num_value, start_line, start_column)
            
            # If we get here, an invalid suffix was used
            self.error("Invalid integer literal suffix: '%s'" % suffix)
         
        # Check for decimal point (for float literals)
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

    def parse_int_suffix(self):
        """Parse integer literal suffixes (u, l, ul, lu)"""
        suffix = ""
        
        # Read first character
        if self.current_char in ['u', 'U']:
            suffix += 'u'
            self.advance()
            # Check for 'l' or 'L' after 'u'
            if self.current_char in ['l', 'L']:
                suffix += 'l'
                self.advance()
        elif self.current_char in ['l', 'L']:
            suffix += 'l'
            self.advance()
            # Check for 'u' or 'U' after 'l'
            if self.current_char in ['u', 'U']:
                suffix += 'u'
                self.advance()
        else:
            self.error("Expected integer literal suffix")
        
        return suffix.lower()  # Normalize to lowercase

    def identifier(self):
        """
        Parse an identifier or keyword using the global KEYWORDS hashtable.
        
        Valid identifiers start with a letter or underscore and can contain 
        letters, digits, or underscores.
        
        Keywords are checked against the global KEYWORDS dictionary.
        """
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
                       (message, self.token.line, self.token.column,
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
        # Use the token-to-type mapping or raise an error for unknown types
        if token_type not in TOKEN_TO_TYPE_MAP:
            self.error("Unknown token type for variable type conversion: %s" % str(token_type))
        return TOKEN_TO_TYPE_MAP[token_type]

    def check_type_compatibility(self, var_name, expr_type):
        """Check if the expression's type is compatible with the variable's type"""
        # Get variable type
        var_type = self.var_types.get(var_name)
        
        # Only check compatibility when both types are known
        if var_type is not None and var_type != TYPE_UNKNOWN and expr_type != TYPE_UNKNOWN and var_type != expr_type:
            self.error("Type mismatch: can't assign a value of type %s to %s (type %s)" %
                      (var_type_to_string(expr_type), var_name, var_type_to_string(var_type)))

    def determine_result_type(self, left_type, right_type):
        """Determine the result type of a binary operation based on operand types"""
        if left_type != right_type:
            self.error("Type mismatch: cannot operate on values of different types")
        return left_type

    def nud(self, t):
        # Handle number literals using the type mapping
        if t.type in TOKEN_TO_TYPE_MAP:
            return NumberNode(t.value, TOKEN_TO_TYPE_MAP[t.type])
            
        if t.type == TT_IDENT:
            var_name = t.value
            
            # For a variable in an expression context:
            # Check if variable has been declared
            if var_name not in self.variables:
                self.error("Variable '%s' is not declared" % var_name)
                
            # Get the variable type
            var_type = self.var_types.get(var_name, TYPE_UNKNOWN)
            return VariableNode(var_name, var_type)
            
        if t.type in [TT_MINUS, TT_NOT, TT_BITNOT]:  # Unary operators
            expr = self.expression(UNARY_PRECEDENCE)
            return UnaryOpNode(t.value, expr, expr.expr_type)
            
        if t.type == TT_LPAREN:
            expr = self.expression(0)
            self.consume(TT_RPAREN)
            return expr
            
        raise Exception('Unexpected token type %d' % t.type)

    def led(self, t, left):
        # Handle assignment as an operator
        if t.type == TT_ASSIGN and left.node_type == AST_NODE_VARIABLE:
            # Get variable name from left side
            var_name = left.name
            var_type = self.var_types.get(var_name, TYPE_UNKNOWN)
            
            # Check if variable is a constant (declared with 'let')
            if var_name in self.constants:
                self.error("Cannot reassign to constant '%s'" % var_name)
                
            # Parse the right side expression
            right = self.expression(0)
            
            # For assignments in conditions (e.g. while x = y do),
            # use the fully resolved types
            if right.node_type == AST_NODE_VARIABLE:
                right_var = right.name
                right_type = self.var_types.get(right_var, right.expr_type)
            
            # Check type compatibility
            self.check_type_compatibility(var_name, right.expr_type)
            
            return AssignNode(var_name, right, var_type)
            
        if t.type in [TT_PLUS, TT_MINUS, TT_MULT, TT_DIV, TT_MOD, TT_SHL, TT_SHR]:
            right = self.expression(self.lbp(t))
            
            # If types don't match, we need to fail
            if left.expr_type != right.expr_type and left.expr_type != TYPE_UNKNOWN and right.expr_type != TYPE_UNKNOWN:
                self.error("Type mismatch in binary operation: %s and %s" % 
                          (var_type_to_string(left.expr_type), var_type_to_string(right.expr_type)))
            
            # Determine result type based on operands using the TYPE_PRECEDENCE list
            if left.expr_type != TYPE_UNKNOWN and left.expr_type == right.expr_type:
                result_type = left.expr_type
            else:
                result_type = TYPE_INT
                # Use the type with the highest precedence
                for t in TYPE_PRECEDENCE:
                    if left.expr_type == t or right.expr_type == t:
                        result_type = t
                        break
            
            return BinaryOpNode(t.value, left, right, result_type)
            
        elif t.type in [TT_EQ, TT_NE, TT_GE, TT_LE, TT_LT, TT_GT]:
            right = self.expression(self.lbp(t))
            # Comparisons always return an integer (0/1 representing false/true)
            return CompareNode(t.value, left, right)
            
        elif t.type in [TT_AND, TT_OR]:
            right = self.expression(self.lbp(t))
            # Logical operations always return an integer (0/1 representing false/true)
            return LogicalNode(t.value, left, right)
            
        elif t.type in [TT_XOR, TT_BITOR, TT_BITAND]:
            right = self.expression(self.lbp(t))
            # Bit operations are performed on integers and return integers
            return BitOpNode(t.value, left, right)
            
        raise Exception('Unexpected token type %d' % t.type)

    def parse_type(self):
        """Parse a type annotation or return None if not present"""
        if self.token.type == TT_COLON:
            self.advance()  # Consume the colon

            # Check if token is a valid type token
            if self.token.type in TYPE_TOKEN_MAP:
                var_type = TYPE_TOKEN_MAP[self.token.type]
                self.advance()  # Consume the type token
                return var_type
            else:
                self.error("Expected type name after ':'")
        return TYPE_UNKNOWN

    def statement(self):
        # Handle empty statements (lone semicolons)
        if self.token.type == TT_SEMI:
            self.advance()  # Skip the semicolon
            return EmptyNode()
        
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
                if expr.node_type == AST_NODE_NUMBER:
                    var_type = expr.expr_type
                elif expr.node_type == AST_NODE_VARIABLE:
                    # Get type from referenced variable
                    ref_var = expr.name
                    var_type = self.var_types.get(ref_var, TYPE_UNKNOWN)
                    if var_type == TYPE_UNKNOWN:
                        self.error("Cannot infer type from variable '%s' with unknown type" % ref_var)
                elif hasattr(expr, 'expr_type'):
                    var_type = expr.expr_type
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
                
                # Check type compatibility with expression type
                if expr.expr_type != TYPE_UNKNOWN and var_type != expr.expr_type:
                    self.error("Type mismatch in initialization: can't assign %s to %s (type %s)" % 
                              (var_type_to_string(expr.expr_type), var_name, var_type_to_string(var_type)))
                    
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
            return VarDeclNode(decl_type, var_name, var_type, expr)
            
        if self.token.type == TT_IF:
            self.advance()
            condition = self.expression(0)
            self.consume(TT_DO)
            then_body = []
            while self.token.type not in [TT_ELSE, TT_END]:
                stmt = self.statement()
                then_body.append(stmt)
            
            # Handle regular if-end or if-end else
            if self.token.type == TT_END:
                self.advance()
                # Check for else after end
                if self.token.type == TT_ELSE:
                    self.advance()
                    else_body = []
                    
                    # Handle both "else if" and "else do" cases
                    if self.token.type == TT_IF:
                        # Parse the nested if as part of else body
                        else_body.append(self.statement())
                    elif self.token.type == TT_DO:
                        # Regular else do...end block
                        self.advance()  # Consume the DO
                        while self.token.type != TT_END:
                            else_body.append(self.statement())
                        self.consume(TT_END)
                    else:
                        self.error("Expected 'if' or 'do' after 'else'")
                    
                    return IfNode(condition, then_body, else_body)
                return IfNode(condition, then_body, None)
            else:
                # We found ELSE without END - error
                self.error("Expected 'end' before 'else'")
                
            return IfNode(condition, then_body, None)  # Should never reach here
        elif self.token.type == TT_WHILE:
            self.advance()
            condition = self.expression(0)
            self.consume(TT_DO)
            body = []
            while self.token.type != TT_END:
                body.append(self.statement())
            self.consume(TT_END)
            return WhileNode(condition, body)
        elif self.token.type == TT_PRINT:
            self.advance()
            expr = self.expression(0)
            self.check_statement_end()
            return PrintNode(expr)
        elif self.token.type == TT_BREAK:
            self.advance()
            self.check_statement_end()
            return BreakNode()
        elif self.token.type == TT_CONTINUE:
            self.advance()
            self.check_statement_end()
            return ContinueNode()
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
                
                # Check type compatibility for all assignments
                self.check_type_compatibility(var, expr.expr_type)
                
                # For compound operators, use CompoundAssignNode
                if op != TT_ASSIGN:
                    self.check_statement_end()
                    return CompoundAssignNode(op, var, expr, var_type)
                    
                # Regular assignment
                self.check_statement_end()
                return AssignNode(var, expr, var_type)
            # Handle expression statements (e.g., an identifier by itself)
            var_type = self.var_types.get(var, TYPE_UNKNOWN)
            expr = VariableNode(var, var_type)
            self.check_statement_end()
            return ExprStmtNode(expr)
        elif self.token.type in [TT_INT_LITERAL, TT_UINT_LITERAL, TT_LONG_LITERAL, TT_ULONG_LITERAL, 
                                TT_FLOAT_LITERAL, TT_LPAREN, TT_MINUS, TT_NOT, TT_BITNOT]:
            # Also handle expressions that start with other tokens
            expr = self.expression(0)
            self.check_statement_end()
            return ExprStmtNode(expr)
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

def run(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    try:
        program = parser.parse()
        env = {}
        ast = program
        for node in program:
            node.eval(env)
        return {'success': True, 'env': env, 'ast': ast}
    except Exception as e:
        return {'success': False, 'error': str(e), 'ast': None}

# Define token type names for debugging
TOKEN_NAMES = {v: k for k, v in globals().items() if k.startswith('TT_')}

def token_name(token_type):
    """Convert a token type number to its name for better debugging"""
    return TOKEN_NAMES.get(token_type, str(token_type))
