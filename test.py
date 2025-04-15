# Test framework for compiler.py
from compiler import *

def test():
    # Test cases with expected final env state
    test_cases = [
        {
            # Tests assignment expression in while condition (not a comparison)
            "code": "var x = 0; var y = 0; while x = y do y = y + 1; end;",
            "expected_env": {"x": 0, "y": 0}
        },
        {
            # Tests operator precedence in expressions (* has higher precedence than +)
            "code": "var x = 5 + 3 * 2;",
            "expected_env": {"x": 11}
        },
        {
            # Tests basic if statement with equality comparison
            "code": "var x = 1; if x == 1 do print x; end", 
            "expected_env": {"x": 1}
        },
        {
            # Tests if-else statement (true condition branch taken)
            "code": "var x = 1; var result = 0; if x == 1 do result = x; else do result = 0; end",
            "expected_env": {"x": 1, "result": 1}
        },
        {
            # Tests bitwise OR operator (|)
            "code": "var x = 5 | 3;", 
            "expected_env": {"x": 7}
        },
        {
            # Tests bitwise AND operator (&)
            "code": "var x = 5 & 3;", 
            "expected_env": {"x": 1}
        },
        {
            # Tests combination of bitwise operations with variable references
            "code": "var x = 5 | 3; var y = x & 2;",
            "expected_env": {"x": 7, "y": 2}
        },
        {
            # Tests logical AND in if condition (evaluates to false)
            "code": "var x = 1; var y = 0; var result = 0; if x and y do result = x; end", 
            "expected_env": {"x": 1, "y": 0, "result": 0}
        },
        {
            # Tests XOR operator with keywords
            "code": "var x = 5 xor 3;",
            "expected_env": {"x": 6}  # 5 xor 3 = 6
        },
        {
            # Tests XOR operator with variable references
            "code": "var x = 7; var y = x xor 2;",
            "expected_env": {"x": 7, "y": 5}  # 7 xor 2 = 5
        },
        {
            # Tests bitwise NOT unary operator
            "code": "var x = 15; var y = bitnot 3;", 
            "expected_env": {"x": 15, "y": -4}
        },
        {
            # Tests else-if construct (first false, second true)
            "code": "var x = 1; var result = 0; if x == 0 do result = 0; else if x == 1 do result = 1; end",
            "expected_env": {"x": 1, "result": 1}
        },
        {
            # Tests multiple else-if branches (first & second false, third true)
            "code": "var x = 3; if x == 1 do print 1; else if x == 2 do print 2; else if x == 3 do print 3; end",
            "expected_env": {"x": 3}
        },
        {
            # Tests nested if statements inside else-if
            "code": "var x = 2; if x == 1 do print 1; else if x == 2 do if x == 2 do print 22; end else do print 3; end",
            "expected_env": {"x": 2}
        },
        {
            # Tests basic while loop with comparison operator
            "code": "var x = 0; while x < 5 do x = x + 1; end",
            "expected_env": {"x": 5}
        },
        {
            # Tests while loop with multiple statements in body
            "code": "var x = 0; var y = 0; while x < 3 do y = y + x; x = x + 1; end",
            "expected_env": {"x": 3, "y": 3}  # y = 0+0 + 0+1 + 1+2 = 3
        },
        {
            # Tests while loop with decrementing counter
            "code": "var x = 10; while x > 0 do x = x - 2; end",
            "expected_env": {"x": 0}
        },
        {
            # Tests more complex while loop with multiplication and addition
            "code": "var x = 1; var y = 1; while x < 10 do x = x * 2; y = y + x; end",
            "expected_env": {"x": 16, "y": 31}  # y = 1+2 + 2+4 + 6+8 + 14+16 = 31
        },
        {
            # Tests break statement in while loop
            "code": "var x = 0; while x < 10 do x = x + 1; if x == 5 do break; end end",
            "expected_env": {"x": 5}
        },
        {
            # Tests break statement with calculations before exit
            "code": "var sum = 0; var x = 0; while x < 10 do x = x + 1; if x > 5 do break; end sum = sum + x; end",
            "expected_env": {"sum": 15, "x": 6}  # sum = 1+2+3+4+5 = 15
        },
        {
            # Tests continue statement to skip an iteration
            "code": "var sum = 0; var x = 0; while x < 5 do x = x + 1; if x == 3 do continue; end sum = sum + x; end",
            "expected_env": {"sum": 12, "x": 5}  # sum = 1+2+4+5 = 12 (3 is skipped)
        },
        {
            # Tests continue with modulo to calculate only even numbers
            "code": "var evens = 0; var x = 0; while x < 10 do x = x + 1; if x % 2 != 0 do continue; end evens = evens + x; end",
            "expected_env": {"evens": 30, "x": 10}  # evens = 2+4+6+8+10 = 30
        },
        {
            # Tests both continue and break in same loop
            "code": "var x = 0; var sum = 0; while x < 10 do x = x + 1; if x < 5 do continue; end if x > 8 do break; end sum = sum + x; end",
            "expected_env": {"x": 9, "sum": 26}  # sum = 5+6+7+8 = 26
        },
        {
            # Tests multiple semicolons (should be treated as empty statements)
            "code": "var x = 5;;; var y = 10;;;",
            "expected_env": {"x": 5, "y": 10}
        },
        {
            # Tests newlines as statement separators (instead of semicolons)
            "code": "var x = 5\nvar y = 10\nvar z = x + y",
            "expected_env": {"x": 5, "y": 10, "z": 15}
        },
        {
            # Tests mixed use of semicolons properly
            "code": "var x = 1; var y = 2; var z = 3;",
            "expected_env": {"x": 1, "y": 2, "z": 3}
        },
        {
            # Tests mixed style of statement separation (newlines and semicolons)
            "code": "var a = 1;\nvar b = 2\nvar c = 3",
            "expected_env": {"a": 1, "b": 2, "c": 3}
        },
        {
            # Tests multiple statements on same line with semicolons
            "code": "var a = 1; var b = 2; var c = 3",
            "expected_env": {"a": 1, "b": 2, "c": 3}
        },
        {
            # Tests missing semicolon but on different lines (should work)
            "code": "var x = 5 + 3",
            "expected_env": {"x": 8}
        },
        {
            # Tests compound assignment operator +=
            "code": "var x = 5; x += 3;",
            "expected_env": {"x": 8}
        },
        {
            # Tests compound assignment operator -=
            "code": "var x = 10; x -= 4;",
            "expected_env": {"x": 6}
        },
        {
            # Tests compound assignment operator *=
            "code": "var x = 3; x *= 5;",
            "expected_env": {"x": 15}
        },
        {
            # Tests compound assignment operator /=
            "code": "var x = 20; x /= 4;",
            "expected_env": {"x": 5}
        },
        {
            # Tests compound assignment operator %=
            "code": "var x = 17; x %= 5;",
            "expected_env": {"x": 2}
        },
        {
            # Tests multiple compound assignments in sequence
            "code": "var x = 1; var y = 2; x += y; y *= 3;",
            "expected_env": {"x": 3, "y": 6}
        },
        {
            # Tests shift left operator
            "code": "var x = 5; var y = x shl 2;", # 5 << 2 = 20
            "expected_env": {"x": 5, "y": 20}
        },
        {
            # Tests shift right operator
            "code": "var x = 20; var y = x shr 2;", # 20 >> 2 = 5
            "expected_env": {"x": 20, "y": 5}
        },
        {
            # Tests var declaration and simple expression
            "code": "var x = 10; var y = x + 5;",
            "expected_env": {"x": 10, "y": 15}
        },
        {
            # Tests let declaration (constant) used in an expression
            "code": "let x = 10; var y = x + 5;",
            "expected_env": {"x": 10, "y": 15}
        },
        {
            # Tests mixing var and let declarations
            "code": "var x = 5; let y = 10; var z = x + y;",
            "expected_env": {"x": 5, "y": 10, "z": 15}
        },
        {
            # Tests reassignment to a var-declared variable
            "code": "var x = 1; x = x + 1;",
            "expected_env": {"x": 2}
        },
    ]
    
    # Test cases that are expected to fail
    fail_test_cases = [
        {
            # Tests error when using variable without declaration
            "code": "x = 5;",  # Missing var or let declaration
            "expected_error": "Variable 'x' is not declared"
        },
        {
            # Tests error when declaring variable without initialization
            "code": "var x; x = 5;",  # Missing initialization
            "expected_error": "Variable declaration must include an initialization"
        },
        {
            # Tests error when using undeclared variable in a logical expression
            "code": "var x = 1; if !x or x and y do print x; end",
            "expected_error": "Variable 'y' is not declared"
        },
        {
            # Tests error when using undeclared variable in print statement
            "code": "print z;",
            "expected_error": "Variable 'z' is not declared"
        },
        {
            # Tests error when using undeclared variable in if condition
            "code": "if x do print 1; end",
            "expected_error": "Variable 'x' is not declared" 
        },
        {
            # Tests error when missing semicolon between statements on the same line
            "code": "var x = 5 + 3 print x;",
            "expected_error": "Expected semicolon between statements"
        },
        {
            # Tests error when missing semicolon between statements on the same line
            "code": "var a = 1 var b = 2",
            "expected_error": "Expected semicolon between statements"
        },
        {
            # Tests error when reassigning to a let-declared constant
            "code": "let x = 5; x = 10;",
            "expected_error": "Cannot reassign to constant 'x'"
        },
        {
            # Tests error when using compound assignment on a let-declared constant
            "code": "let x = 5; x += 10;",
            "expected_error": "Cannot reassign to constant 'x'"
        },
        {
            # Tests error when using undeclared variable in initialization
            "code": "var x = y;",
            "expected_error": "Variable 'y' is not declared"
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

if __name__ == '__main__':
    test()
