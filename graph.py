import ast

EXCLUDED_FUNCTIONS = {
    "abs", "all", "any", "ascii", "bin", "bool", "callable", "chr", "classmethod", 
    "complex", "delattr", "dict", "dir", "divmod", "enumerate", "eval", "filter", 
    "float", "format", "frozenset", "getattr", "globals", "hasattr", "hash", "help", 
    "hex", "id", "input", "int", "isinstance", "issubclass", "iter", "len", "list", 
    "locals", "map", "max", "min", "next", "object", "oct", "open", "ord", "pow", 
    "print", "property", "range", "repr", "reversed", "round", "set", "setattr", 
    "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", 
    "vars", "zip", "__import__"
}
def generate_sequence_diagram(filename: str, text_output_filename: str):
    with open(filename, "r") as f:
        source = f.read()

    function_details = extract_function_details(source)
    
    diagram = []

    # Determine the main function dynamically
    try:
        main_func = max(function_details, key=lambda k: len(function_details[k]['calls']))
    except:
        exit('no main function found')

    if main_func in function_details:
        try:    
            for called_function in function_details[main_func]['calls']:
                params_str = ''
                if called_function in function_details:
                    params_str = function_details[called_function]['params']
                call_str = f"{main_func}->{called_function}: {params_str}"
                diagram.append(call_str)

                # Add return value
                if function_details[called_function]['return_type']:
                    return_str = f"{main_func}<--{called_function}: {function_details[called_function]['return_type']}"
                    diagram.append(return_str)

                # Add docstring note of the called function to the diagram right after its call
                if function_details[called_function]['docstring']:
                    comment_str = f"note over {called_function}:{function_details[called_function]['docstring'].splitlines()[0]}"  # Only first line
                    diagram.append(comment_str)
        except:
            pass

    # Now handle other functions
    for func_name, details in function_details.items():
        if func_name == main_func:
            continue  # Already handled above

        for called_function in details['calls']:
            params_str = ''
            if called_function in function_details:
                params_str = function_details[called_function]['params']
            call_str = f"{func_name}->{called_function}: {params_str}"
            diagram.append(call_str)

            # Add return value
            if function_details.get(called_function, {}).get('return_type'):
                return_str = f"{func_name}<--{called_function}: {function_details[called_function]['return_type']}"
                diagram.append(return_str)

            # Add docstring note of the called function to the diagram right after its call
            if function_details.get(called_function, {}).get('docstring'):
                comment_str = f"note over {called_function}:{function_details[called_function]['docstring'].splitlines()[0]}"  # Only first line
                diagram.append(comment_str)
    
    with open(text_output_filename, 'w') as f:
        for line in diagram:
            f.write(line + '\n')


class ExtendedFunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_details = {}
        self.current_function = None

    def _get_annotation(self, annotation: ast.AST) -> str:
        if annotation:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
        return ''

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.current_function = node.name
        
        params = []
        for arg in node.args.args:
            param_type = self._get_annotation(arg.annotation)
            params.append(f"{arg.arg} ({param_type})" if param_type else arg.arg)
        params_str = ", ".join(params)

        return_type = self._get_annotation(node.returns)

        docstring = ast.get_docstring(node) or ""

        self.function_details[node.name] = {
            'params': params_str,
            'return_type': return_type,
            'calls': [],
            'docstring': docstring
        }
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and self.current_function and node.func.id not in EXCLUDED_FUNCTIONS:
            self.function_details[self.current_function]['calls'].append(node.func.id)
        self.generic_visit(node)

def extract_function_details(source_code: str) -> dict:
    tree = ast.parse(source_code)
    visitor = ExtendedFunctionVisitor()
    visitor.visit(tree)
    return visitor.function_details

if __name__ == "__main__":
    file = 'AIPodcaster\main.py'
    generate_sequence_diagram(file, f"{file}.txt")
