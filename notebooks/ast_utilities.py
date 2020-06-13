import ast

LITERAL_CONSTANT_AST_NODES = (ast.Str, ast.Num, ast.Constant, ast.FormattedValue,
                             ast.Bytes, ast.NameConstant, ast.List, ast.Tuple,
                             ast.Set, ast.Dict)

def only_literal_constants(node):
    for child in ast.walk(node):
        if isinstance(child, ast.Name): #not isinstance(child, LITERAL_CONSTANT_AST_NODES):
            return False
    return True

def assignment_of_literal(assignment, parameters: [str]):
    for target in assignment.targets:
        if isinstance(target, ast.Name):
            if target.id in parameters:
                if only_literal_constants(assignment.value):
                    return target.id
    return False




def function_with_reinitialization(code):
    try:
        tree = ast.parse(code)
    except:
        return None
    for exp in tree.body:
        if isinstance(exp, ast.FunctionDef):
            parameters = [arg.arg for arg in exp.args.args]
            for statement in exp.body:
                if isinstance(statement, ast.Assign):
                    result = assignment_of_literal(statement, parameters)
                    if result:
                        return result
    return False


def find_calls(code, name):
    try:
        tree = ast.parse(code)
    except:
        return None
    for child in ast.walk(tree):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == name:
                return True
    return False
    
def count_function_definitions(code):
    try:
        tree = ast.parse(code)
    except:
        return None
    count = 0
    for child in ast.walk(tree):
        if isinstance(child, ast.FunctionDef):
            count += 1
    return count
    

def find_returns(code):
    try:
        tree = ast.parse(code)
    except:
        return None
    for child in ast.walk(tree):
        if isinstance(child, ast.Return):
            return True
    return False

def decomposed_function(code):
    try:
        tree = ast.parse(code)
    except:
        return False
    functions = {}
    # Map function names => called function names
    for i, exp in enumerate(tree.body):
        if isinstance(exp, ast.FunctionDef):
            function_name = exp.name
            functions[function_name] = set()
            for child in ast.walk(exp):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        call_name = child.func.id
                        functions[function_name].add(call_name)
    # Determine whether any called functions exist in the function names
    for definer, called_functions in functions.items():
        for callee in called_functions:
            if callee != definer and callee in functions:
                return True
    return False
