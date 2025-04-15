# Implementation of C-like operators for our interpreter
# This file contains functions that emulate C operator behavior

# Import type constants from compiler.py
from __future__ import division  # Use true division
from shared import *

# Helper functions for type handling
def is_integer_type(type_):
    """Check if a type is any integer type (signed or unsigned)"""
    return type_ in [TYPE_INT, TYPE_UINT, TYPE_LONG, TYPE_ULONG]

def is_unsigned_type(type_):
    """Check if a type is unsigned"""
    return type_ in [TYPE_UINT, TYPE_ULONG]

def is_signed_type(type_):
    """Check if a type is signed"""
    return type_ in [TYPE_INT, TYPE_LONG]

def is_float_type(type_):
    """Check if a type is floating point"""
    return type_ == TYPE_FLOAT

# Binary arithmetic operators
def add(left, right, left_type, right_type):
    """Addition with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return float(left) + float(right)
    return int(left) + int(right)

def subtract(left, right, left_type, right_type):
    """Subtraction with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return float(left) - float(right)
    return int(left) - int(right)

def multiply(left, right, left_type, right_type):
    """Multiplication with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return float(left) * float(right)
    return int(left) * int(right)

def divide(left, right, left_type, right_type):
    """Division with C semantics"""
    if right == 0:
        raise ZeroDivisionError("Division by zero")
        
    if is_float_type(left_type) or is_float_type(right_type):
        return float(left) / float(right)
        
    # Integer division - follow C rules
    if is_unsigned_type(left_type) and is_unsigned_type(right_type):
        # Both unsigned, use integer division
        return int(left) // int(right)
    elif is_signed_type(left_type) and is_signed_type(right_type):
        # Both signed, use C truncation toward zero
        result = abs(left) // abs(right)
        if (left < 0) != (right < 0):  # If signs differ
            return -result
        return result
    else:
        # Mixed signed/unsigned - follow C promotion rules
        # We'll treat as unsigned if either operand is unsigned
        return int(left) // int(right)

def modulo(left, right, left_type, right_type):
    """Modulus with C semantics"""
    if right == 0:
        raise ZeroDivisionError("Modulo by zero")
        
    if is_float_type(left_type) or is_float_type(right_type):
        raise TypeError("Modulo not defined for floating point types")
        
    # Integer modulo - follow C rules
    if is_unsigned_type(left_type) and is_unsigned_type(right_type):
        # Both unsigned
        return int(left) % int(right)
    elif is_signed_type(left_type) and is_signed_type(right_type):
        # Both signed - C99 requires sign of result to match dividend
        result = abs(left) % abs(right)
        if left < 0:
            return -result
        return result
    else:
        # Mixed signed/unsigned - follow C promotion rules
        return int(left) % int(right)

def shift_left(left, right, left_type, right_type):
    """Left shift with C semantics"""
    if right < 0:
        raise ValueError("Negative shift count")
    return int(left) << int(right)

def shift_right(left, right, left_type, right_type):
    """Right shift with C semantics"""
    if right < 0:
        raise ValueError("Negative shift count")
        
    # In C, right shift behavior depends on whether the left operand is signed
    if is_signed_type(left_type) and left < 0:
        # Arithmetic shift (preserve sign bit) for signed negative values
        # Python's >> already does this
        return int(left) >> int(right)
    else:
        # Logical shift (fill with zeros) for unsigned or positive values
        # For positive values, Python's >> is equivalent
        return int(left) >> int(right)

# Unary operators
def negate(value, type_):
    """Unary negation with C semantics"""
    if is_float_type(type_):
        return -float(value)
    return -int(value)

def logical_not(value):
    """Logical NOT with C semantics - returns 1 for false, 0 for true"""
    return 1 if not value else 0

def bitwise_not(value, type_):
    """Bitwise NOT with C semantics"""
    return ~int(value)

# Comparison operators
def compare_eq(left, right, left_type, right_type):
    """Equality comparison with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return 1 if float(left) == float(right) else 0
    return 1 if int(left) == int(right) else 0

def compare_ne(left, right, left_type, right_type):
    """Not equal comparison with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return 1 if float(left) != float(right) else 0
    return 1 if int(left) != int(right) else 0

def compare_lt(left, right, left_type, right_type):
    """Less than comparison with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return 1 if float(left) < float(right) else 0
    
    # For integers, handle sign differences according to C rules
    if is_signed_type(left_type) and is_unsigned_type(right_type):
        # Signed < Unsigned: if left is negative, result is true, else compare as unsigned
        if int(left) < 0:
            return 1
    elif is_unsigned_type(left_type) and is_signed_type(right_type):
        # Unsigned < Signed: if right is negative, result is false, else compare as unsigned
        if int(right) < 0:
            return 0
    
    return 1 if int(left) < int(right) else 0

def compare_le(left, right, left_type, right_type):
    """Less than or equal comparison with C semantics"""
    if is_float_type(left_type) or is_float_type(right_type):
        return 1 if float(left) <= float(right) else 0
    
    # For integers, handle sign differences according to C rules
    if is_signed_type(left_type) and is_unsigned_type(right_type):
        # Signed <= Unsigned: if left is negative, result is true, else compare as unsigned
        if int(left) < 0:
            return 1
    elif is_unsigned_type(left_type) and is_signed_type(right_type):
        # Unsigned <= Signed: if right is negative, result is false, else compare as unsigned
        if int(right) < 0:
            return 0
    
    return 1 if int(left) <= int(right) else 0

def compare_gt(left, right, left_type, right_type):
    """Greater than comparison with C semantics"""
    return 1 - compare_le(left, right, left_type, right_type)

def compare_ge(left, right, left_type, right_type):
    """Greater than or equal comparison with C semantics"""
    return 1 - compare_lt(left, right, left_type, right_type)

# Logical operators
def logical_and(left, right):
    """Logical AND with C semantics"""
    return 1 if left and right else 0

def logical_or(left, right):
    """Logical OR with C semantics"""
    return 1 if left or right else 0

# Bitwise operators
def bitwise_and(left, right, left_type, right_type):
    """Bitwise AND with C semantics"""
    return int(left) & int(right)

def bitwise_or(left, right, left_type, right_type):
    """Bitwise OR with C semantics"""
    return int(left) | int(right)

def bitwise_xor(left, right, left_type, right_type):
    """Bitwise XOR with C semantics"""
    return int(left) ^ int(right)
