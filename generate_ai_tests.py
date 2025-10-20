# generate_ai_tests.py
import os
import ast
import time
from pathlib import Path
from openai import OpenAI

# 设置 OpenAI API Key（在系统环境变量中）
# openai.api_key = os.getenv("OPENAI_API_KEY")

# 项目目录
SRC_DIR = Path(__file__).parent / "app"
OUTPUT_DIR = Path(__file__).parent / "tests/ai_generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS_FILE = Path(__file__).parent / "targets.txt"

def read_targets():
    """读取 targets.txt，返回 [("app/models.py", "User.verify_password"), ...]"""
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
    """解析 Python AST，提取指定函数/方法源码"""
    abs_path = os.path.join(SRC_DIR, filepath)
    with open(abs_path, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == target_name.split(".")[0]:
                # 如果是类，查找方法
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
    解析 Python AST，提取指定函数或方法源码。
    如果是类中的方法，则返回整个类的源码。

    target_name 支持格式：
    - "module.py::function_name"
    - "module.py::ClassName.method_name"
    """
    abs_path = os.path.join(SRC_DIR, filepath)
    with open(abs_path, "r") as f:
        source = f.read()

    tree = ast.parse(source)

    # 处理可能的类方法 target
    if "." in target_name:
        class_name, method_name = target_name.split(".")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # 找到方法，确认类中包含目标方法
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                        # 返回整个类源码
                        return ast.get_source_segment(source, node)
        return None  # 没找到对应类或方法
    else:
        # 目标是函数或类本身
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == target_name:
                return ast.get_source_segment(source, node)

    return None

def read_python_file(file_path: str) -> str:
    """
    读取 Python 文件内容并返回字符串。

    Args:
        file_path (str): Python 文件的绝对或相对路径

    Returns:
        str: 文件的完整代码内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
        IOError: 文件读取失败时抛出
    """
    # 检查文件存在性
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # 确保是 Python 文件
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
        model="gpt-4o-mini",  # 可以换成 gpt-4.1/gpt-5 等
        messages=[
            {"role": "system", "content": "You are an expert Python testing assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        top_p=0.9
    )

    return response.choices[0].message.content

def save_tests(test_code, target_name):
    """保存测试代码到 tests/ai_generated/"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"test_{target_name.replace('.', '_')}.py"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        f.write("import pytest\n\n")
        f.write(test_code.strip())
    print(f"[+] Saved AI tests -> {path}")


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    targets = read_targets()
    for filepath, target in targets:
        if target:  # 针对函数/方法
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
