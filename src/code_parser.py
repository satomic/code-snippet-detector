import os
import ast
from git import Repo
import traceback
from src.utils.log_utils import *

class CodeParser:

    def parse_repository(self, repo_url: str):
        """克隆仓库并解析所有代码文件"""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join("data/repos", repo_name)
        if not os.path.exists(repo_path):
            Repo.clone_from(repo_url, repo_path)
        
        code_blocks = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    code_blocks.extend(self._parse_python(file_path))
                    logger.info(f"Found {len(code_blocks)} code blocks in {file_path}")
        return code_blocks

    def _parse_python(self, file_path: str):
        """解析Python文件获取函数/类"""
        with open(file_path, "r", encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
                functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        try:
                            functions.append({
                                "type": "function",
                                "name": node.name,
                                "code": ast.unparse(node),
                                "file": file_path
                            })
                            logger.info(f"[{file_path}] Found function {node.name}")
                        except Exception as e:
                            logger.error(f"Error parsing function {node.name} in {file_path}: {e}")
                classes = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        try:
                            classes.append({
                                "type": "class",
                                "name": node.name,
                                "code": ast.unparse(node),
                                "file": file_path
                            })
                            logger.info(f"[{file_path}] Found class {node.name}")
                        except Exception as e:
                            logger.error(f"Error parsing class {node.name} in {file_path}: {e}")
                return functions + classes
            except:
                print(traceback.format_exc())
                return []