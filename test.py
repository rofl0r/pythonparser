# Test framework for compiler.py
from compiler import *

def test():
    # Test cases with expected final env state
    test_cases = [
        {
            "code": "var x = 0; var y = 0; while x = y do y = y + 1; end; print x;",
            "expected_env": {"x": 0, "y": 0}
        },
        {
            "code": "var x = 5 + 3 * 2; print x;",
            "expected_env": {"x": 11}
        },
        {
            "code": "var x = 1; if x == 1 do print x; end", 
            "expected_env": {"x": 1}
        },
        {
            "code": "var x = 1; if x == 1 do print x; else do print 0; end",
            "expected_env": {"x": 1}
        },
        {
            "code": "var x = 5 | 3; print x;", 
            "expected_env": {"x": 7}
        },
        {
            "code": "var x = 5 & 3; print x;", 
            "expected_env": {"x": 1}
        },
        {
            "code": "var x = 5 | 3; var y = x & 2; print y;",
            "expected_env": {"x": 7, "y": 2}
        },
        {
            "code": "var x = 1; var y = 0; if x and y do print x; end", 
            "expected_env": {"x": 1, "y": 0}
        },
        {
            "code": "var x = 5 xor 3; print x;",
            "expected_env": {"x": 6}  # 5 xor 3 = 6
        },
        {
            "code": "var x = 7; var y = x xor 2; print y;",
            "expected_env": {"x": 7, "y": 5}  # 7 xor 2 = 5
        },
        {
            "code": "var x = 15; var y = bitnot 3; print y;", 
            "expected_env": {"x": 15, "y": -4}
        },
        {
            "code": "var x = 1; if x == 0 do print 0; else if x == 1 do print 1; end",
            "expected_env": {"x": 1}
        },
        {
            "code": "var x = 3; if x == 1 do print 1; else if x == 2 do print 2; else if x == 3 do print 3; end",
            "expected_env": {"x": 3}
        },
        {
            "code": "var x = 2; if x == 1 do print 1; else if x == 2 do if x == 2 do print 22; end else do print 3; end",
            "expected_env": {"x": 2}
        },
        # While loop test cases
        {
            "code": "var x = 0; while x < 5 do x = x + 1; end print x;",
            "expected_env": {"x": 5}
        },
        {
            "code": "var x = 0; var y = 0; while x < 3 do y = y + x; x = x + 1; end",
            "expected_env": {"x": 3, "y": 3}  # y = 0+0 + 0+1 + 1+2 = 3
        },
        {
            "code": "var x = 10; while x > 0 do x = x - 2; end",
            "expected_env": {"x": 0}
        },
        {
            "code": "var x = 1; var y = 1; while x < 10 do x = x * 2; y = y + x; end",
            "expected_env": {"x": 16, "y": 31}  # y = 1+2 + 2+4 + 6+8 + 14+16 = 31
        },
        # Break statement tests
        {
            "code": "var x = 0; while x < 10 do x = x + 1; if x == 5 do break; end end",
            "expected_env": {"x": 5}
        },
        {
            "code": "var sum = 0; var x = 0; while x < 10 do x = x + 1; if x > 5 do break; end sum = sum + x; end",
            "expected_env": {"sum": 15, "x": 6}  # sum = 1+2+3+4+5 = 15
        },
        # Continue statement tests
        {
            "code": "var sum = 0; var x = 0; while x < 5 do x = x + 1; if x == 3 do continue; end sum = sum + x; end",
            "expected_env": {"sum": 12, "x": 5}  # sum = 1+2+4+5 = 12 (3 is skipped)
        },
        {
            "code": "var evens = 0; var x = 0; while x < 10 do x = x + 1; if x % 2 != 0 do continue; end evens = evens + x; end",
            "expected_env": {"evens": 30, "x": 10}  # evens = 2+4+6+8+10 = 30
        },
        {
            "code": "var x = 0; var sum = 0; while x < 10 do x = x + 1; if x < 5 do continue; end if x > 8 do break; end sum = sum + x; end",
            "expected_env": {"x": 9, "sum": 26}  # sum = 5+6+7+8 = 26
        },
        {
            "code": "var x = 5;;; var y = 10;;;",  # Test multiple semicolons
            "expected_env": {"x": 5, "y": 10}
        },
        {
            "code": "var x = 5\nvar y = 10\nvar z = x + y",  # Test newlines instead of semicolons
            "expected_env": {"x": 5, "y": 10, "z": 15}
        },
        {
            "code": "var x = 1; var y = 2; var z = 3;",  # Mix of with/without semicolons
            "expected_env": {"x": 1, "y": 2, "z": 3}
        },
        {
            "code": "var a = 1;\nvar b = 2\nvar c = 3",  # New lines instead of semicolons
            "expected_env": {"a": 1, "b": 2, "c": 3}
        },
        {
            "code": "var a = 1; var b = 2; var c = 3",  # Semicolons on the same line - should work
            "expected_env": {"a": 1, "b": 2, "c": 3}
        },
        {
            "code": "var x = 5 + 3\nprint x",  # Missing semicolon but on different lines - should work
            "expected_env": {"x": 8}
        },
        # Compound assignment operators tests
        {
            "code": "var x = 5; x += 3; print x;",
            "expected_env": {"x": 8}
        },
        {
            "code": "var x = 10; x -= 4; print x;",
            "expected_env": {"x": 6}
        },
        {
            "code": "var x = 3; x *= 5; print x;",
            "expected_env": {"x": 15}
        },
        {
            "code": "var x = 20; x /= 4; print x;",
            "expected_env": {"x": 5}
        },
        {
            "code": "var x = 17; x %= 5; print x;",
            "expected_env": {"x": 2}
        },
        {
            "code": "var x = 1; var y = 2; x += y; y *= 3; print x; print y;", 
            "expected_env": {"x": 3, "y": 6}
        },
        {
            "code": "var x = 5; var y = x shl 2; print y;", # 5 << 2 = 20
            "expected_env": {"x": 5, "y": 20}
        },
        {
            "code": "var x = 20; var y = x shr 2; print y;", # 20 >> 2 = 5
            "expected_env": {"x": 20, "y": 5}
        },
        # Test var and let declarations
        {
            "code": "var x = 10; var y = x + 5; print y;",
            "expected_env": {"x": 10, "y": 15}
        },
        {
            "code": "let x = 10; var y = x + 5; print y;",
            "expected_env": {"x": 10, "y": 15}
        },
        {
            "code": "var x = 5; let y = 10; var z = x + y; print z;",
            "expected_env": {"x": 5, "y": 10, "z": 15}
        },
        {
            "code": "var x = 1; x = x + 1; print x;",
            "expected_env": {"x": 2}
        },
    ]
    
    # Test cases that are expected to fail
    fail_test_cases = [
        {
            "code": "x = 5;",  # Missing var or let declaration
            "expected_error": "Variable 'x' is not declared"
        },
        {
            "code": "var x; x = 5;",  # Missing initialization
            "expected_error": "Variable declaration must include an initialization"
        },
        {
            "code": "var x = 1; if !x or x and y do print x; end",
            "expected_error": "Variable 'y' is not declared"
        },
        {
            "code": "print z;",
            "expected_error": "Variable 'z' is not declared"
        },
        {
            "code": "if x do print 1; end",
            "expected_error": "Variable 'x' is not declared" 
        },
        {
            "code": "var x = 5 + 3 print x;",  # Missing semicolon between statements on the same line
            "expected_error": "Expected semicolon between statements"
        },
        {
            "code": "var a = 1 var b = 2",  # No semicolon between statements on the same line
            "expected_error": "Expected semicolon between statements"
        },
        {
            "code": "let x = 5; x = 10;",  # Trying to reassign to a constant
            "expected_error": "Cannot reassign to constant 'x'"
        },
        {
            "code": "let x = 5; x += 10;",  # Trying to modify a constant with compound assignment
            "expected_error": "Cannot reassign to constant 'x'"
        },
        {
            "code": "var x = y;",  # Using undeclared variable in initialization
            "expected_error": "Variable 'y' is not declared"
        },
        {
            "code": "var z = 5; let z = 10;", # Redeclaring a variable
            "expected_error": "already declared"  # Should add proper error message for this case
        },
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
