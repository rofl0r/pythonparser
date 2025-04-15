# Test framework for compiler.py
from compiler import *

def test():
    # Test cases with expected final env state
    test_cases = [
        # Regular test cases (expected to succeed)
        # Each has "code" and "expected_env"
        {
            # Tests variable declaration with type inference (:=)
            "code": "var x := 5;",
            "expected_env": {"x": 5}
        },
        {
            # Tests float literal with type inference
            "code": "var y := 3.14;",
            "expected_env": {"y": 3.14}
        },
        {
            # Tests explicit int type annotation
            "code": "var x: int = 10;",
            "expected_env": {"x": 10}
        },
        {
            # Tests explicit float type annotation
            "code": "var y: float = 2.718;",
            "expected_env": {"y": 2.718}
        },
        {
            # Tests let with type inference
            "code": "let x := 42;",
            "expected_env": {"x": 42}
        },
        {
            # Tests assignment of same type variable
            "code": "var x := 5; var y := x;",
            "expected_env": {"x": 5, "y": 5}
        },
        {
            # Tests assignment expression in while condition (not a comparison)
            "code": "var x := 0; var y := 0; while x = y do y = y + 1; end;",
            "expected_env": {"x": 0, "y": 0}
        },
        {
            # Tests operator precedence in expressions (* has higher precedence than +)
            "code": "var x := 5 + 3 * 2;",
            "expected_env": {"x": 11}
        },
        {
            # Tests basic if statement with equality comparison
            "code": "var x := 1; if x == 1 do print x; end", 
            "expected_env": {"x": 1}
        },
        {
            # Tests if-else statement (true condition branch taken)
            "code": "var x := 1; var result := 0; if x == 1 do result = x; end else do result = 0; end",
            "expected_env": {"x": 1, "result": 1}
        },
        {
            # Tests bitwise OR operator (|)
            "code": "var x := 5 | 3;", 
            "expected_env": {"x": 7}
        },
        {
            # Tests bitwise AND operator (&)
            "code": "var x := 5 & 3;", 
            "expected_env": {"x": 1}
        },
        {
            # Tests combination of bitwise operations with variable references
            "code": "var x := 5 | 3; var y := x & 2;",
            "expected_env": {"x": 7, "y": 2}
        },
        {
            # Tests logical AND in if condition (evaluates to false)
            "code": "var x := 1; var y := 0; var result := 0; if x and y do result = x; end", 
            "expected_env": {"x": 1, "y": 0, "result": 0}
        },
        {
            # Tests XOR operator with keywords
            "code": "var x := 5 xor 3;",
            "expected_env": {"x": 6}  # 5 xor 3 = 6
        },
        {
            # Tests XOR operator with variable references
            "code": "var x := 7; var y := x xor 2;",
            "expected_env": {"x": 7, "y": 5}  # 7 xor 2 = 5
        },
        {
            # Tests bitwise NOT unary operator
            "code": "var x := 15; var y := bitnot 3;", 
            "expected_env": {"x": 15, "y": -4}
        },
        {
            # Tests else-if construct (first false, second true)
            "code": "var x := 1; var result := 0; if x == 0 do result = 0; end else if x == 1 do result = 1; end",
            "expected_env": {"x": 1, "result": 1}
        },
        {
            # Tests multiple else-if branches (first & second false, third true)
            "code": "var x := 3; if x == 1 do print 1; end else if x == 2 do print 2; end else if x == 3 do print 3; end",
            "expected_env": {"x": 3}
        },
        {
            # Tests mixed int and float operations
            "code": "var x: int = 5; var y: float = 2.5; var z := y;", 
            "expected_env": {"x": 5, "y": 2.5, "z": 2.5}  # Variable declaration with inferred type from another variable
        },
        {
            # Tests int division
            "code": "var x := 10; var y := 3; var z := x / y;",
            "expected_env": {"x": 10, "y": 3, "z": 3}  # Integer division
        },
        {
            # Tests float division
            "code": "var x := 10.0; var y := 3.0; var z := x / y;",
            "expected_env": {"x": 10.0, "y": 3.0, "z": 3.3333333333333335}  # Float division
        },
        {
            # Tests assignment as expression in while condition
            "code": "var x := 10; var y := 0; while (y = y + 1) < 5 do x -= 1; end",
            # y will end up as 5 (the condition becomes false when y = 5)
            # x will be decremented 4 times (while y is 1,2,3,4)
            "expected_env": {"x": 6, "y": 5}
        },
        {
           "name": "uint variable declaration and operations",
           "code": """
               var x : uint = 42;
               var y := 10u;
               var z : uint = x + y;
               print z;
               z = z / 2;
               print z;
               z = z * 3;
               print z;
           """,
           "expected_env": {"x": 42, "y": 10, "z": 78}
        },
        {
           "name": "long variable declaration and operations",
           "code": """
               var x : long = 42l;
               var y := 10l;
               var z : long = x + y;
               print z;
               z = z / 2;
               print z;
               z = z * 3;
               print z;
           """,
           "expected_env": {"x": 42, "y": 10, "z": 78}
        },
        {
           "name": "ulong variable declaration and operations",
           "code": """
               var x : ulong = 42ul;
               var y := 10ul;
               var z : ulong = x + y;
               print z;
               z = z / 2;
               print z;
               z = z * 3;
               print z;
           """,
           "expected_env": {"x": 42, "y": 10, "z": 78}
        },
        {
           "name": "mixed types variable declaration - type inference",
           "code": """
               var a := 42;     // int
               var b := 42u;    // uint
               var c := 42l;    // long
               var d := 42ul;   // ulong
               var e := 42.0;   // float
               
               // Test assignments to explicitly typed variables
               var x : int = 10;
               var y : uint = 20u;
               var z : long = 30l;
               var w : ulong = 40ul;
               var v : float = 50.0;
               
               print a;
               print b;
               print c;
               print d;
               print e;
           """,
           "expected_env": {"a": 42, "b": 42, "c": 42, "d": 42, "e": 42.0,
                        "x": 10, "y": 20, "z": 30, "w": 40, "v": 50.0}
        },
        {
           "name": "unsigned int division",
           "code": """
               var x : uint = 10u;
               var y : uint = 3u;
               var z : uint = x / y;  // Should be 3 (truncated)
               print z;
           """,
           "expected_env": {"x": 10, "y": 3, "z": 3}
        },
        {
           "name": "signed division with negative numbers",
           "code": """
               var x : int = -10;
               var y : int = 3;
               var z : int = x / y;  // Should be -3 (truncated toward zero)
               print z;
               
               var a : int = 10;
               var b : int = -3;
               var c : int = a / b;  // Should be -3
               print c;
               
               var m : int = -10;
               var n : int = -3;
               var o : int = m / n;  // Should be 3
               print o;
           """,
           "expected_env": {"x": -10, "y": 3, "z": -3, 
                        "a": 10, "b": -3, "c": -3, 
                        "m": -10, "n": -3, "o": 3}
        },
        {
           "name": "assignment in expression-condition",
           "code": """
               var a : uint = 0u;
               
               if a = 5u do
                   print a;
               end
               
               var b : long = 0l;
               if b = 10l do
                   print b;
               end
               
               var c : ulong = 0ul;
               if c = 15ul do
                   print c;
               end
           """,
           "expected_env": {"a": 5, "b": 10, "c": 15}
        },

        # Test cases that are expected to fail
        # Each has "code" and "expected_error"

        {
            # Tests error when trying to assign float to int
            "code": "var x := 1; var y := 0.1; x = y;",
            "expected_error": "Type mismatch: can't assign a value of type float to x (type int)"
        },
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
            "code": "var x := 1; if !x or x and y do print x; end",
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
            "code": "var x := 5 + 3 print x;",
            "expected_error": "Expected semicolon between statements"
        },
        {
            # Tests error when missing semicolon between statements on the same line
            "code": "var a := 1 var b := 2",
            "expected_error": "Expected semicolon between statements"
        },
        {
            # Tests error when reassigning to a let-declared constant
            "code": "let x := 5; x = 10;",
            "expected_error": "Cannot reassign to constant 'x'"
        },
        {
            # Tests error when using compound assignment on a let-declared constant
            "code": "let x := 5; x += 10;",
            "expected_error": "Cannot reassign to constant 'x'"
        },
        {
            # Tests error when using undeclared variable in initialization
            "code": "var x := y;",
            "expected_error": "Variable 'y' is not declared"
        },
        {
            # Tests error when using = without explicit type
            "code": "var x = 5;",
            "expected_error": "requires explicit type annotation"
        },
        {
            # Tests error when assigning float to int variable
            "code": "var x: int = 5; var y: float = 2.5; x = y;",
            "expected_error": "Type mismatch"
        },
        {
            # Tests error when redeclaring a variable
            "code": "var x := 5; var x := 10;",
            "expected_error": "already declared"
        },
        {
            # Tests float literal without decimal digits
            "code": "var x := 5.;",
            "expected_error": "Invalid float literal"
        },
        {
            # Tests else-if without proper end before else
            "code": "var x := 3; if x == 1 do print 1; else if x == 2 do print 2; else if x == 3 do print 3; end",
            "expected_error": "Expected 'end' before 'else'"
        },
        {
            # Tests error when mixing int and float types in binary operation
            # This test expects a failure since our language doesn't allow implicit type conversion
            "code": "var x := 10; var y := 3.0; var z := x / y;", 
            "expected_error": "Type mismatch in binary operation"
        },
    ]

    # List to track failing tests
    failed_tests = []

    # Run all test cases
    for i, test_case in enumerate(test_cases):
        test_num = i + 1
        print("\nTest %d:" % test_num)
        print("Input: %s" % test_case["code"])
        
        result = run(test_case["code"])
        
        # Check if this test is expected to fail
        if "expected_error" in test_case:
            # This is a test that should fail
            if not result['success'] and test_case["expected_error"] in result['error']:
                print("Success! Failed with expected error: %s" % result['error'])
            else:
                print("Test didn't fail as expected! Result: %s" % result)
                failed_tests.append(test_num)
                # Add AST dump for unexpected failures
                if result.get('ast'):
                    print("AST dump: %s" % result['ast'])
            
        else:
            # This is a test that should succeed
            if result['success']:
                # Check if environment values match
                env_match = True
                for k, v in test_case["expected_env"].iteritems():
                    if k not in result['env'] or result['env'][k] != v:
                        env_match = False
                        break
                
                if env_match:
                    print("Success! Environment matches expectations.")
                else:
                    print("Test passed but with incorrect environment values:")
                    print("  Expected env: %s" % test_case["expected_env"])
                    print("  Actual env: %s" % result['env'])
                    failed_tests.append(test_num)
            else:
                print("Failed! Error: %s" % result['error'])
                failed_tests.append(test_num)
                if result.get('ast'):
                    print("AST dump: %s" % result['ast'])

    # Print statistics at the end
    print("\n========== Test Results ==========")
    print("Total tests: %d" % len(test_cases))
    print("Failed test IDs: %s" % (", ".join(str(num) for num in failed_tests) if failed_tests else "None"))
    print("All tests passed: %s" % ("No" if failed_tests else "Yes"))

if __name__ == '__main__':
    test()
