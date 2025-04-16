# Implementation of a Pratt parser in Python 2.7

from interpreter import add, subtract, multiply, divide, modulo, shift_left, shift_right, negate
from interpreter import logical_not, bitwise_not, logical_and, logical_or, bitwise_and, bitwise_or, bitwise_xor
from interpreter import compare_eq, compare_ne, compare_ge, compare_gt, compare_lt, compare_le
from shared import *

# Base class for all AST nodes
class ASTNode(object):
    def __init__(self, node_type=AST_NODE_BASE):
        self.node_type = node_type
        self.expr_type = TYPE_UNKNOWN

    def eval(self, env):
        raise CompilerException("Evaluation not implemented for this node")

    def __repr__(self):
        return "%s" % ast_node_type_to_string(self.node_type)

class NumberNode(ASTNode):
    def __init__(self, value, expr_type):
        ASTNode.__init__(self, AST_NODE_NUMBER)
        self.value = value
        self.expr_type = expr_type  # TYPE_INT, TYPE_FLOAT, TYPE_UINT, TYPE_LONG, TYPE_ULONG

    def eval(self, env):
        return self.value

    def __repr__(self):
        return "Number(%s, %s)" % (self.value, var_type_to_string(self.expr_type))

class StringNode(ASTNode):
    def __init__(self, value):
        ASTNode.__init__(self, AST_NODE_STRING)
        self.value = value
        self.expr_type = TYPE_STRING

    def eval(self, env):
        return self.value

    def __repr__(self):
        return "String(\"%s\")" % self.value

class VariableNode(ASTNode):
    def __init__(self, name, var_type):
        ASTNode.__init__(self, AST_NODE_VARIABLE)
        self.name = name
        self.expr_type = var_type

    def eval(self, env):
        if self.name not in env:
            raise CompilerException("Variable '%s' is not defined" % self.name)
        return env[self.name]

    def __repr__(self):
        return "Var(%s, %s)" % (self.name, var_type_to_string(self.expr_type))

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
            # Handle string concatenation
            if self.left.expr_type == TYPE_STRING and self.right.expr_type == TYPE_STRING:
                return left_val + right_val
                
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

    def __repr__(self):
        return "BinaryOp(%s, %s, %s) -> %s" % (
            self.operator, repr(self.left), repr(self.right),
            var_type_to_string(self.expr_type)
        )

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

    def __repr__(self):
        return "UnaryOp(%s, %s) -> %s" % (
            self.operator, repr(self.operand), var_type_to_string(self.expr_type)
        )

class AssignNode(ASTNode):
    def __init__(self, var_name, expr, var_type):
        ASTNode.__init__(self, AST_NODE_ASSIGN)
        self.var_name = var_name
        self.expr = expr
        self.expr_type = var_type
        
    def eval(self, env):
        value = self.expr.eval(env)
        
        # Check if type promotion is needed and allowed
        if self.expr_type != self.expr.expr_type:
            if not can_promote(self.expr.expr_type, self.expr_type):
                raise CompilerException("Cannot assign %s to %s"%(var_type_to_string(self.expr.expr_type), var_type_to_string(self.expr_type)))
                
        # Handle number literal promotion
        if self.expr.node_type == AST_NODE_NUMBER:
            value = promote_literal_if_needed(value, self.expr.expr_type, self.expr_type)
        
        env[self.var_name] = value
        return value

    def __repr__(self):
        return "Assign(%s, %s) -> %s" % (
            self.var_name, repr(self.expr), var_type_to_string(self.expr_type)
        )

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
            # Handle string concatenation for += operator
            if self.expr_type == TYPE_STRING:
                if self.expr.expr_type != TYPE_STRING:
                    raise CompilerException("Cannot use += with string and %s" % var_type_to_string(self.expr.expr_type))
                return env.update({self.var_name: current_value + expr_value}) or (current_value + expr_value)
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

    def __repr__(self):
        op_name = token_name(self.op_type)
        return "CompoundAssign(%s, %s, %s) -> %s" % (
            op_name, self.var_name, repr(self.expr), var_type_to_string(self.expr_type)
        )

class PrintNode(ASTNode):
    def __init__(self, expr):
        ASTNode.__init__(self, AST_NODE_PRINT)
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        print(value)
        return value

    def __repr__(self):
        return "Print(%s)" % repr(self.expr)

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

    def __repr__(self):
        if self.else_body:
            return "If(%s, [%s], [%s])" % (
                repr(self.condition),
                ", ".join(repr(stmt) for stmt in self.then_body),
                ", ".join(repr(stmt) for stmt in self.else_body),
            )
        else:
            return "If(%s, [%s])" % (
                repr(self.condition),
                ", ".join(repr(stmt) for stmt in self.then_body),
            )

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

    def __repr__(self):
        return "While(%s, [%s])" % (
            repr(self.condition),
            ", ".join(repr(stmt) for stmt in self.body),
        )

class BreakNode(ASTNode):
    def __init__(self):
        ASTNode.__init__(self, AST_NODE_BREAK)

    def eval(self, env):
        raise BreakException()

    def __repr__(self):
        return "Break()"

class ContinueNode(ASTNode):
    def __init__(self):
        ASTNode.__init__(self, AST_NODE_CONTINUE)

    def eval(self, env):
        raise ContinueException()

    def __repr__(self):
        return "Continue()"

class ExprStmtNode(ASTNode):
    def __init__(self, expr):
        ASTNode.__init__(self, AST_NODE_EXPR_STMT)
        self.expr = expr

    def eval(self, env):
        return self.expr.eval(env)

    def __repr__(self):
        return "ExprStmt(%s)" % repr(self.expr)

class VarDeclNode(ASTNode):
    def __init__(self, decl_type, var_name, var_type, expr):
        ASTNode.__init__(self, AST_NODE_VAR_DECL)
        self.decl_type = decl_type
        self.var_name = var_name
        self.var_type = var_type
        self.expr = expr

    def eval(self, env):
        value = self.expr.eval(env)
        
        # Check if type promotion is needed and allowed
        if self.var_type != self.expr.expr_type:
            if not can_promote(self.expr.expr_type, self.var_type):
                raise CompilerException("Cannot assign %s to %s"%(var_type_to_string(self.expr.expr_type), var_type_to_string(self.var_type)))

        # For variable declarations, literals get special treatment
        # This supports writing code like: var x:uint = 42; (without 'u' suffix)
        if self.expr.node_type == AST_NODE_NUMBER:
            # No actual value transformation needed for most numeric types
            pass
        
        env[self.var_name] = value
        return value

    def __repr__(self):
        decl_type_str = "var" if self.decl_type == TT_VAR else "let"
        return "VarDecl(%s, %s, %s, %s)" % (
            decl_type_str, self.var_name, var_type_to_string(self.var_type), repr(self.expr)
        )

class EmptyNode(ASTNode):
    def __init__(self):
        ASTNode.__init__(self, AST_NODE_EMPTY)

    def eval(self, env):
        return 0

    def __repr__(self):
        return "Empty()"

class FunctionDeclNode(ASTNode):
    def __init__(self, name, params, return_type, body):
        ASTNode.__init__(self, AST_NODE_FUNCTION_DECL)
        self.name = name
        self.params = params  # List of (name, type) tuples
        self.return_type = return_type
        self.body = body
        self.expr_type = return_type

    def eval(self, env):
        # Store function in the environment
        env[self.name] = self
        return 0

    def __repr__(self):
        params_str = ", ".join(["%s:%s" % (name, var_type_to_string(ptype)) for name, ptype in self.params])
        return "Function(%s(%s):%s, [%s])" % (
            self.name, 
            params_str, 
            var_type_to_string(self.return_type), 
            ", ".join(repr(stmt) for stmt in self.body),
        )

class ReturnNode(ASTNode):
    def __init__(self, expr=None):
        ASTNode.__init__(self, AST_NODE_RETURN)
        self.expr = expr  # Can be None for return with no value
        self.expr_type = TYPE_VOID if expr is None else (expr.expr_type if hasattr(expr, 'expr_type') else TYPE_UNKNOWN)

    def eval(self, env):
        value = None if self.expr is None else self.expr.eval(env)
        # Throw a special exception to unwind the call stack
        raise ReturnException(value)

    def __repr__(self):
        if self.expr:
            return "Return(%s)" % repr(self.expr)
        else:
            return "Return()"

class FunctionCallNode(ASTNode):
    def __init__(self, name, args):
        ASTNode.__init__(self, AST_NODE_FUNCTION_CALL)
        self.name = name
        self.args = args
        self.expr_type = TYPE_UNKNOWN  # Will be set during type checking

    def eval(self, env):
        # Get function from environment
        if self.name not in env:
            raise CompilerException("Function '%s' is not defined" % self.name)
        
        func = env[self.name]
        if not isinstance(func, FunctionDeclNode):
            raise CompilerException("'%s' is not a function" % self.name)
        
        # Create a new local scope for function execution
        local_env = Environment(parent=env)
        
        # Evaluate arguments and bind to parameters
        if len(self.args) != len(func.params):
            raise CompilerException("Function '%s' expects %d arguments, got %d" % 
                                  (self.name, len(func.params), len(self.args)))
        
        for (param_name, param_type), arg in zip(func.params, self.args):
            arg_value = arg.eval(env)
            local_env[param_name] = arg_value
        
        try:
            # Execute function body
            for stmt in func.body:
                stmt.eval(local_env)
            
            # If no return statement was encountered and function is not void,
            # we should raise an error
            if func.return_type != TYPE_VOID:
                raise CompilerException("Function '%s' has non-void return type but reached end of function without return" % self.name)
            
            # For void functions, return None
            return None
        except ReturnException as ret:
            # Check return value type against function's return type
            if func.return_type == TYPE_VOID and ret.value is not None:
                raise CompilerException("Void function '%s' returned a value" % self.name)
            
            return ret.value

    def __repr__(self):
        args_str = ", ".join(repr(arg) for arg in self.args)
        return "Call(%s(%s))" % (self.name, args_str)

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
        
        # Handle string comparison operations
        if self.left.expr_type == TYPE_STRING and self.right.expr_type == TYPE_STRING:
            if self.operator == '==':
                return 1 if left_val == right_val else 0
            elif self.operator == '!=':
                return 1 if left_val != right_val else 0
            # Other comparison operators are not supported for strings
            elif self.operator in ['>', '>=', '<', '<=']:
                raise CompilerException("Operator %s not supported for strings" % self.operator)
            else:
                # Unknown operator
                raise CompilerException("Unknown comparison operator: %s" % self.operator)
                
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

    def __repr__(self):
        return "Compare(%s, %s, %s)" % (self.operator, repr(self.left), repr(self.right))

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

    def __repr__(self):
        return "Logical(%s, %s, %s)" % (self.operator, repr(self.left), repr(self.right))

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

    def __repr__(self):
        return "BitOp(%s, %s, %s)" % (self.operator, repr(self.left), repr(self.right))

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
            '"': self.handle_string,
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
            ',': self.handle_comma,  # Added for function parameters
        }

    def make_token(self, token_type, value):
        """Helper to create a token with current line and column info"""
        return Token(token_type, value, self.line, self.column)

    def error(self, message="Invalid character"):
        raise CompilerException('%s at line %d, column %d: "%s"' %
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
    def skip_until(self, terminator):
        """
        Skip all characters until the terminator character is found or EOF.
        Does NOT consume the terminator character itself.
        Args:
            terminator: The character to stop at
        """
        while self.current_char is not None and self.current_char != terminator:
            self.advance()
        # Note: At this point, current_char is either None (EOF) or the terminator character
        # We don't advance further, leaving the terminator to be processed by other methods

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
        
    def handle_string(self):
        """Handle string literals"""
        # Record starting position for error reporting
        start_line = self.line
        start_column = self.column
        
        # Skip the opening quote
        self.advance()
        
        # Start collecting string content
        result = ""
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
            
        # Check if we ended because of a closing quote or end of input
        if self.current_char is None:
            self.error("Unterminated string literal")
            
        # Skip the closing quote
        self.advance()
        
        # Create a string token
        return Token(TT_STRING_LITERAL, result, start_line, start_column)

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
        self.advance() # Skip the first '/'
        # Handle C++-style comments
        if self.current_char == '/':
            # Skip first '/'
            self.advance()  # Skip second '/'
            self.skip_until('\n')  # Skip until end of line, but don't consume the newline
            return self.next_token()  # Return the next token after the comment
        elif self.current_char == '=':
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
    
    def handle_comma(self):
        """Handle comma token for function parameters"""
        token = self.make_token(TT_COMMA, ',')
        self.advance()
        return token

    def next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '"':
                return self.handle_string()
                
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
    
class ReturnException(Exception):
    """Raised when a return statement is encountered"""
    def __init__(self, value=None):
        self.value = value

class ContinueException(Exception):
    """Raised when a continue statement is encountered"""
    pass

class Environment(dict):
    def __init__(self, parent=None):
        dict.__init__(self)
        self.parent = parent
    
    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        elif self.parent:
            return self.parent[key]
        raise KeyError(key)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token() # Current token
        self.prev_token = None  # Previous token (for better error messages)
        
        # Per-scope tracking structures
        self.scopes = ["global"]  # Stack of scope names
        self.variables = {"global": set()}  # Track declared variables per scope
        self.constants = {"global": set()}  # Track constants (let declarations) per scope
        self.var_types = {"global": {}}     # Track variable types per scope
        
        self.functions = {}     # Track function declarations (name -> (params, return_type))
        self.current_function = None  # Track current function for return checking

    def enter_scope(self, scope_name):
        """Enter a new scope for variable tracking"""
        self.scopes.append(scope_name)
        self.variables[scope_name] = set()
        self.constants[scope_name] = set()
        self.var_types[scope_name] = {}
    
    def leave_scope(self):
        """Leave the current scope"""
        if len(self.scopes) > 1:  # Don't leave global scope
            self.scopes.pop()
    
    def current_scope(self):
        """Get the current scope name"""
        return self.scopes[-1]
    
    def is_variable_declared(self, var_name):
        """Check if a variable is declared in any accessible scope"""
        # Check all scopes from current to global
        for scope in reversed(self.scopes):
            if var_name in self.variables[scope]:
                return True
        return False
    
    def is_constant(self, var_name):
        """Check if a variable is a constant in any accessible scope"""
        # Check all scopes from current to global
        for scope in reversed(self.scopes):
            if var_name in self.constants[scope]:
                return True
        return False
    
    def get_variable_type(self, var_name):
        """Get a variable's type from the appropriate scope"""
        # Check all scopes from current to global
        for scope in reversed(self.scopes):
            if var_name in self.var_types[scope]:
                return self.var_types[scope][var_name]
        return TYPE_UNKNOWN
    
    def declare_variable(self, var_name, var_type, is_const=False):
        """Declare a variable in the current scope"""
        current = self.current_scope()
        # Check if already declared in current scope
        if var_name in self.variables[current]:
            return False  # Already declared in this scope
            
        self.variables[current].add(var_name)
        self.var_types[current][var_name] = var_type
        if is_const:
            self.constants[current].add(var_name)
        return True
        
    def error(self, message):
        token_type_name = token_name(self.token.type)
        raise CompilerException("%s at line %d, column %d. Token: %s (%s)" %
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
        # Get variable type from the appropriate scope
        var_type = self.get_variable_type(var_name)

        # Check compatibility using can_promote function
        if var_type is not None and var_type != TYPE_UNKNOWN and expr_type != TYPE_UNKNOWN and not can_promote(expr_type, var_type):
            self.error("Type mismatch: can't assign a value of type %s to %s (type %s)" % 
                       (var_type_to_string(expr_type), var_name, var_type_to_string(var_type)))

    def function_declaration(self):
        """Parse a function declaration"""
        self.advance()  # Skip 'def'
        
        # Parse function name
        if self.token.type != TT_IDENT:
            self.error("Expected function name after 'def'")
        name = self.token.value
        self.advance()
        
        # Parse parameters
        self.consume(TT_LPAREN)
        params = []
        if self.token.type != TT_RPAREN:
            params.append(self.parameter())
            while self.token.type == TT_COMMA:
                self.advance()  # Skip comma
                params.append(self.parameter())
        self.consume(TT_RPAREN)
        
        # Parse return type (if specified)
        return_type = TYPE_VOID  # Default to void (implicitly)
        if self.token.type == TT_COLON:
            self.advance()
            if self.token.type in TYPE_TOKEN_MAP:
                return_type = TYPE_TOKEN_MAP[self.token.type]
                self.advance()
            else:
                self.error("Expected type name after ':'")
        
        # Register function
        if name in self.functions:
            self.error("Function '%s' is already defined" % name)
        self.functions[name] = (params, return_type)
        
        # Parse function body
        self.consume(TT_DO)
        
        # Enter function scope
        self.enter_scope(name)
        
        # Add parameters to function scope variables
        for param_name, param_type in params:
            # Check for duplicate parameter names
            if param_name in self.variables[name]:
                self.error("Duplicate parameter name '%s'" % param_name)
            
            # Add parameter to function scope
            self.variables[name].add(param_name)
            self.var_types[name][param_name] = param_type
        
        # Save and set current function for return checking
        prev_function = self.current_function
        self.current_function = name
        
        # Parse function body statements
        body = []
        while self.token.type not in [TT_END, TT_EOF]:
            body.append(self.statement())
        self.consume(TT_END)
        
        # Restore previous context
        self.current_function = prev_function
        self.leave_scope()
        
        return FunctionDeclNode(name, params, return_type, body)

    def parameter(self):
        """Parse a function parameter (name:type)"""
        if self.token.type != TT_IDENT:
            self.error("Expected parameter name")
            
        name = self.token.value
        self.advance()
        
        # Parse type - REQUIRED
        if self.token.type != TT_COLON:
            self.error("Function parameters require explicit type annotation")
        
        self.advance() # Skip colon
        if self.token.type not in TYPE_TOKEN_MAP:
            self.error("Expected type name after ':'")
        
        param_type = TYPE_TOKEN_MAP[self.token.type]
        self.advance()
        
        return (name, param_type)

    def determine_result_type(self, left_type, right_type):
        """Determine the result type of a binary operation based on operand types"""
        if left_type != right_type:
            self.error("Type mismatch: cannot operate on values of different types")
        return left_type

    def nud(self, t):
        # Handle number literals using the type mapping
        if t.type in TOKEN_TO_TYPE_MAP:
            return NumberNode(t.value, TOKEN_TO_TYPE_MAP[t.type])
        
        if t.type == TT_STRING_LITERAL:
            return StringNode(t.value)
            
        if t.type == TT_IDENT:
            var_name = t.value
            
            # For a variable in an expression context:
            # Check if variable has been declared in any accessible scope
            if not self.is_variable_declared(var_name):
                self.error("Variable '%s' is not declared" % var_name)
                
            # Get the variable type from the appropriate scope
            var_type = self.get_variable_type(var_name)
            return VariableNode(var_name, var_type)
            
        if t.type in [TT_MINUS, TT_NOT, TT_BITNOT]:  # Unary operators
            expr = self.expression(UNARY_PRECEDENCE)
            return UnaryOpNode(t.value, expr, expr.expr_type)
            
        if t.type == TT_LPAREN:
            expr = self.expression(0)
            self.consume(TT_RPAREN)
            return expr
            
        raise CompilerException('Unexpected token type %d' % t.type)

    def led(self, t, left):
        # Handle assignment as an operator
        if t.type == TT_ASSIGN and left.node_type == AST_NODE_VARIABLE:
            # Get variable name from left side
            var_name = left.name
            var_type = self.get_variable_type(var_name)
            
            # Check if variable is a constant (declared with 'let')
            if self.is_constant(var_name):
                self.error("Cannot reassign to constant '%s'" % var_name)
                
            # Parse the right side expression
            right = self.expression(0)
            
            # For assignments in conditions (e.g. while x = y do),
            # use the fully resolved types
            if right.node_type == AST_NODE_VARIABLE:
                right_var = right.name
                right_type = self.get_variable_type(right_var)
            
            # Check type compatibility
            self.check_type_compatibility(var_name, right.expr_type)
            
            return AssignNode(var_name, right, var_type)
            
        if t.type in [TT_PLUS, TT_MINUS, TT_MULT, TT_DIV, TT_MOD, TT_SHL, TT_SHR]:
            right = self.expression(self.lbp(t))
            
            # If types don't match, we need to fail
            if left.expr_type != right.expr_type and left.expr_type != TYPE_UNKNOWN and right.expr_type != TYPE_UNKNOWN and not can_promote(right.expr_type, left.expr_type):
                self.error("Type mismatch in binary operation: %s and %s" %
                          (var_type_to_string(left.expr_type), var_type_to_string(right.expr_type)))
            
            # Special handling for string concatenation
            if t.type == TT_PLUS and (left.expr_type == TYPE_STRING or right.expr_type == TYPE_STRING):
                if left.expr_type != TYPE_STRING or right.expr_type != TYPE_STRING:
                    self.error("Cannot concatenate string with non-string type")
                result_type = TYPE_STRING
            # Normal case - determine result type based on operands
            elif left.expr_type != TYPE_UNKNOWN and left.expr_type == right.expr_type:
                result_type = left.expr_type
            else:
                # Use the type with the highest precedence from TYPE_PRECEDENCE list
                for tp in TYPE_PRECEDENCE:
                    if left.expr_type == tp or right.expr_type == tp:
                        result_type = tp
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
            
        raise CompilerException('Unexpected token type %d' % t.type)

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
            
        # Handle function declarations
        if self.token.type == TT_DEF:
            # Only allowed in global scope
            if self.current_function is not None:
                self.error("Nested function declarations are not allowed")
            return self.function_declaration()
            
        # Handle return statements
        if self.token.type == TT_RETURN:
            # Must be inside a function
            if self.current_function is None:
                self.error("'return' statement outside function")
            
            self.advance()
            
            # Return with no value
            if self.token.type in [TT_SEMI, TT_EOF] or (self.prev_token and self.token.line > self.prev_token.line):
                self.check_statement_end()
                return ReturnNode(None)
                
            # Return with value
            expr = self.expression(0)
            
            # Check if return type matches function return type
            func_return_type = self.functions[self.current_function][1]
            if func_return_type == TYPE_VOID:
                self.error("Void function '%s' cannot return a value" % self.current_function)
                
            self.check_statement_end()
            return ReturnNode(expr)
        
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
                    var_type = self.get_variable_type(ref_var)
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
                if expr.expr_type != TYPE_UNKNOWN and var_type != expr.expr_type and not can_promote(expr.expr_type, var_type):
                    self.error("Type mismatch in initialization: can't assign %s to %s (type %s)" % 
                              (var_type_to_string(expr.expr_type), var_name, var_type_to_string(var_type)))
                    
            else:
                self.error("Variable declaration must include an initialization")
            
            # Register the variable as defined in the current scope
            if var_name in self.variables[self.current_scope()]:
                self.error("Variable '%s' is already declared in this scope" % var_name)
                
            # Declare the variable in current scope
            self.declare_variable(var_name, var_type, decl_type == TT_LET)
            
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
            
        # Handle while loop
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

            # Function call
            if self.token.type == TT_LPAREN:
                # Check if function exists
                if var not in self.functions:
                    self.error("Function '%s' is not declared" % var)
                
                self.advance()  # Skip '('
                args = []
                if self.token.type != TT_RPAREN:
                    args.append(self.expression(0))
                    while self.token.type == TT_COMMA:
                        self.advance()  # Skip comma
                        args.append(self.expression(0))
                self.consume(TT_RPAREN)
                
                # Check argument types match parameter types
                func_params, func_return_type = self.functions[var]
                
                # Check number of arguments
                if len(args) != len(func_params):
                    self.error("Function '%s' expects %d arguments, got %d" % 
                              (var, len(func_params), len(args)))
                
                # Check argument types
                for i, ((param_name, param_type), arg) in enumerate(zip(func_params, args)):
                    if arg.expr_type != param_type and not can_promote(arg.expr_type, param_type):
                        self.error("Type mismatch for argument %d of function '%s': expected %s, got %s" %
                                  (i+1, var, var_type_to_string(param_type), var_type_to_string(arg.expr_type)))
                
                self.check_statement_end()
                return FunctionCallNode(var, args)
            
            # Variable reference
            else:
                # Check if variable has been declared
                if not self.is_variable_declared(var):
                    self.error("Variable '%s' is not declared" % var)
                    
                # Handle all assignment operators (regular and compound)
                if self.token.type in [TT_ASSIGN, TT_PLUS_ASSIGN, TT_MINUS_ASSIGN, 
                                      TT_MULT_ASSIGN, TT_DIV_ASSIGN, TT_MOD_ASSIGN]:
                    # Check if variable is a constant (declared with 'let')
                    if self.is_constant(var):
                        self.error("Cannot reassign to constant '%s'" % var)
                
                    op = self.token.type
                    var_type = self.get_variable_type(var)
                
                    # Advance past the operator
                    self.advance()
                
                    # Parse the expression
                    expr = self.expression(0)
                
                    # Check type compatibility for assignments
                    self.check_type_compatibility(var, expr.expr_type)
                
                    # For compound operators, use CompoundAssignNode
                    if op != TT_ASSIGN:
                        self.check_statement_end()
                        return CompoundAssignNode(op, var, expr, var_type)
                    
                    # Regular assignment
                    self.check_statement_end()
                    return AssignNode(var, expr, var_type)
                
                # Handle expression statements (e.g., an identifier by itself)
                var_type = self.get_variable_type(var)
                expr = VariableNode(var, var_type)
                self.check_statement_end()
                return ExprStmtNode(expr)
        elif self.token.type in [TT_INT_LITERAL, TT_UINT_LITERAL, TT_LONG_LITERAL, TT_ULONG_LITERAL, 
                                TT_FLOAT_LITERAL, TT_STRING_LITERAL, TT_LPAREN, TT_MINUS, TT_NOT, TT_BITNOT]:
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
        # Parse the program
        program = parser.parse()
        ast = program
        
        # Create environment for execution
        env = Environment()
        
        # Check if there are any non-function declarations in global scope
        has_global_code = False
        for node in program:
            if node.node_type != AST_NODE_FUNCTION_DECL:
                has_global_code = True
                break
        
        if has_global_code:
            return {'success': False, 'error': 'Code outside of functions is not allowed', 'ast': ast}
        
        # First process all function declarations
        for node in program:
            if node.node_type == AST_NODE_FUNCTION_DECL:
                node.eval(env)
        
        # Check if main function exists
        if "main" not in env:
            return {'success': False, 'error': "No 'main' function defined", 'ast': ast}
        
        # Execute main function
        main_func = env["main"]
        if not isinstance(main_func, FunctionDeclNode):
            return {'success': False, 'error': "'main' is not a function", 'ast': ast}
        
        # Make sure main has no parameters
        if len(main_func.params) > 0:
            return {'success': False, 'error': "Function 'main' cannot have parameters", 'ast': ast}
        
        try:
            # Create a scope for main function
            local_env = Environment(parent=env)
            for stmt in main_func.body:
                stmt.eval(local_env)
                
            return {'success': True, 'env': env, 'ast': ast}
        except ReturnException as ret:
            return {'success': True, 'result': ret.value, 'env': env, 'ast': ast}
    except CompilerException as e:
        return {'success': False, 'error': str(e), 'ast': None}
