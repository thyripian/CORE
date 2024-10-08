import ast
import os
import sys

# Adjust the path to include the 'merlin' directory in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utilities import DevLogger  # isort: skip

# Initialize the DevLogger
dev_log = DevLogger().get_logger()

# List of components (file paths to trace)
components = [
    ("../../core/run_app.py", "Run App Logic"),
    ("../../search_functionality/elastic_query.py", "Elastic Query Logic"),
    ("../../update_functionality/check_updates.py", "Check Updates Logic"),
]

# Specify the base path of your own project
PROJECT_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def should_trace(filename):
    """
    Determines if a file should be traced.
    Only trace files within your own project directory and exclude system or external packages.
    """
    return filename and filename.startswith(PROJECT_BASE_PATH)


def parse_file(filepath, traced_files=None):
    """
    Parse the file for function calls, imports, and class methods using AST.
    Recursively trace imports.
    """
    if traced_files is None:
        traced_files = set()

    try:
        # Open and read the file content
        with open(filepath) as file:
            file_content = file.read()

        # Parse the file content into an AST
        tree = ast.parse(file_content, filepath)

        tab = "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"

        # Log the file being traced
        dev_log.info(f"\n\n*********** TRACE ***********")
        dev_log.info(f"STARTING TRACE FOR FILE: {os.path.basename(filepath)}\n")

        # Keep track of the files we've traced to avoid cycles
        traced_files.add(filepath)

        # Trace imports, function definitions, and function calls
        trace_ast(tree, filepath, traced_files)

        dev_log.info(f"\n\nCOMPLETED TRACE FOR FILE: {os.path.basename(filepath)}")
        dev_log.info("---------------------------------------------------------\n")

    except Exception as e:
        dev_log.error(f"Error parsing file {filepath}: {str(e)}")


def trace_ast(tree, filepath, traced_files):
    """
    Traverse the AST and log imports, function definitions, class definitions, and variable names.
    """
    dev_log.info("\nIMPORTS AND VARIABLE NAMES\n")

    # Initialize a set to keep track of unique variable names to avoid duplicates
    variable_names = set()

    for node in ast.walk(tree):
        # Handle Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                dev_log.info(
                    f"IMPORT: {alias.name.upper()} in {os.path.basename(filepath).upper()}"
                )
                trace_imported_file(alias.name, traced_files)

        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module:
                dev_log.info(
                    f"IMPORT FROM: {module.upper()} in {os.path.basename(filepath).upper()}"
                )
                trace_imported_file(module, traced_files)

        # Handle Variable Assignments
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_names.add(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            variable_names.add(elt.id)

        # Handle Function Definitions
        elif isinstance(node, ast.FunctionDef):
            dev_log.info(
                f"\nFUNCTION DEFINITION: {node.name.upper()} in {os.path.basename(filepath).upper()} at line {node.lineno}"
            )
            trace_function_body(node, filepath, traced_files)

        # Handle Class Definitions
        elif isinstance(node, ast.ClassDef):
            dev_log.info(
                f"\nCLASS DEFINITION: {node.name.upper()} in {os.path.basename(filepath).upper()} at line {node.lineno}"
            )
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    dev_log.info(
                        f"  METHOD: {sub_node.name.upper()} in class {node.name.upper()} at line {sub_node.lineno}"
                    )
                    trace_function_body(sub_node, filepath, traced_files)

    # Log all variables found after imports and definitions
    if variable_names:
        dev_log.info("\nVARIABLES DEFINED IN FILE:")
        for var_name in sorted(variable_names):
            dev_log.info(
                f"VARIABLE: {var_name.upper()} in {os.path.basename(filepath).upper()}"
            )

        dev_log.info("\nEND OF VARIABLE LIST\n")


def trace_function_body(node, filepath, traced_files):
    """
    Trace the body of a function or method to identify function calls.
    Recursively trace the imported modules as well.
    """
    for sub_node in ast.walk(node):
        if isinstance(sub_node, ast.Call):
            func_name = get_function_name(sub_node)
            dev_log.info(
                f"CALL: {func_name.upper()} in {os.path.basename(filepath).upper()} at line {sub_node.lineno}"
            )

            # If the function is imported from another file, trace it
            trace_imported_file(func_name, traced_files)


def get_function_name(node):
    """
    Extract the function name from an AST call node, handling more complex scenarios.
    """
    try:
        # Handle simple function call: foo()
        if isinstance(node.func, ast.Name):
            return node.func.id

        # Handle method or attribute call: obj.method()
        elif isinstance(node.func, ast.Attribute):
            # Recursively get the base object name: obj.method -> obj
            return f"{get_function_name(node.func.value)}.{node.func.attr}"

        # Handle subscript call: obj[index]
        elif isinstance(node.func, ast.Subscript):
            return f"{get_function_name(node.func.value)}[subscript]"

        # Handle lambda or other callable objects
        elif isinstance(node.func, ast.Lambda):
            return "<lambda>"

        # Handle calls to callables, where the call itself is an argument: (foo())()
        elif isinstance(node.func, ast.Call):
            return f"({get_function_name(node.func)})"

        # Fallback for unknown node types
        else:
            return "<unknown function>"
    except AttributeError as e:
        # Log the error and return a placeholder if we can't retrieve the function name
        # dev_log.error(f"Error retrieving function name: {str(e)}")
        return "<unknown function>"


def trace_imported_file(module_name, traced_files):
    """
    Trace the imported module if it exists in the project directory.
    """
    module_path = module_name.replace(".", "/") + ".py"
    full_path = os.path.join(PROJECT_BASE_PATH, module_path)

    if (
        os.path.exists(full_path)
        and should_trace(full_path)
        and full_path not in traced_files
    ):
        dev_log.info(f"Tracing imported file: {full_path}")
        parse_file(full_path, traced_files)


def run_trace_for_all_components():
    """
    Iterate through the list of files and trace each one.
    """
    dev_log.info(f"Starting the tracing process for {len(components)} components.")
    traced_files = set()  # Track the files we've already traced
    for filepath, name in components:
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), filepath))
        dev_log.info(f"Tracing component: {name}")
        parse_file(full_path, traced_files)
    dev_log.info("Completed tracing all components.")


if __name__ == "__main__":
    run_trace_for_all_components()
