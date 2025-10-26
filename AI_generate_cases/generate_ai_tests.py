# generate_ai_tests.py
import os
import ast
import time
from pathlib import Path
from openai import OpenAI

# project dir
SRC_DIR = Path(__file__).parent / "app"
OUTPUT_DIR = Path(__file__).parent / "tests/ai_generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS_FILE = Path(__file__).parent / "targets.txt"

def read_targets():
    """read targets.txt，return [("app/models.py", "User.verify_password"), ...]"""
    targets = []
    with open(TARGETS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("::")
            if len(parts) == 2:
                targets.append((parts[0], parts[1]))  # (文件, 函数/方法)
            else:
                targets.append((line, None))  # 整个文件
    return targets


def extract_function_source1(filepath, target_name):
    """Parse Python AST，extract the source code of the specified function/method"""
    abs_path = os.path.join(SRC_DIR, filepath)
    with open(abs_path, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == target_name.split(".")[0]:
                # If it is a class, search the method
                if isinstance(node, ast.ClassDef) and "." in target_name:
                    method_name = target_name.split(".")[1]
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            return ast.get_source_segment(source, item)
                else:
                    return ast.get_source_segment(source, node)

    return None


def extract_function_source(filepath, target_name):
    """
    Parse Python AST，Extract the source code of the specified function or method.
    If it is a method within a class, then return the entire source code of the class.

    target_name Support format：
    - "module.py::function_name"
    - "module.py::ClassName.method_name"
    """
    abs_path = os.path.join(SRC_DIR, filepath)
    with open(abs_path, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    # Handle possible class methods target
    if "." in target_name:
        class_name, method_name = target_name.split(".")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Find a method to verify that the class contains the target method
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                        # return source code
                        return ast.get_source_segment(source, node)
        return None  # No corresponding class or method was found.
    else:
        # The goal is the function or the class itself
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == target_name:
                return ast.get_source_segment(source, node)

    return None

def read_python_file(file_path: str) -> str:
    """
    Read the content of the Python file and return it as a string.

    Args:
        file_path (str): Python The absolute or relative path of the file

    Returns:
        str: The complete code content of the file

    Raises:
        FileNotFoundError: Throws an exception when the file does not exist.
        IOError: Throws an exception when file reading fails.
    """
    # Check the existence of the file
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Make sure a Python file
    if not file_path.endswith(".py"):
        raise ValueError("Only Python files (.py) are supported.")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    return code

def generate_tests_with_ai(source_code, target_name, api_key):
    """using OpenAI create pytest testcase"""
    prompt = f"""
You are given the following Python code from the Flasky project:

{source_code}

Generate python unittest case for the function/class `{target_name}`.
Ensure:
- Each test is a standalone function
- Use assert statements
- Do not modify the original code
- Only output Python test functions (no explanations)
"""

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert Python testing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        top_p=0.9
    )

    return response.choices[0].message.content

def save_tests(test_code, target_name):
    """Save the test code to tests/ai_generated/"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"test_{target_name.replace('.', '_')}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        f.write("import pytest\n\n")
        f.write(test_code.strip())
    print(f"[+] Saved AI tests -> {path}")


def main():
    api_key = os.getenv("OPENAI_API_KEY") # Obtain the API key from the environment variables
    targets = read_targets()
    for filepath, target in targets:
        if target:
            code = extract_function_source(filepath, target)
            if not code:
                print(f"[!] Could not find {target} in {filepath}")
                continue
            timestamp_int = int(time.time())
            print(timestamp_int)
            tests = generate_tests_with_ai(code, target, api_key)
            timestamp_int = int(time.time())
            print(timestamp_int)
            save_tests(tests, target)
        else:
            print(f"[!] Whole-file generation not yet implemented for {filepath}")

# def main():
#     file_path="./app/api/authentication.py"
#     code=read_python_file(file_path)
#     target = "get_token"
#     timestamp_int = int(time.time())
#     print(timestamp_int)
#     tests = generate_tests_with_ai(code, target)
#     timestamp_int = int(time.time())
#     print(timestamp_int)
#     save_tests(tests,target)

if __name__ == "__main__":
    main()
