import os
import pytest
from src.code_parser import CodeParser

@pytest.fixture
def sample_repo_path():
    return os.path.join(os.path.dirname(__file__), "test_utils/sample_repo")

def test_parse_repository_clones_repo(tmpdir, mocker):
    """测试仓库克隆功能"""
    mock_clone = mocker.patch("git.Repo.clone_from")
    parser = CodeParser()
    parser.parse_repository("https://github.com/fake/repo.git")
    mock_clone.assert_called_once_with(
        "https://github.com/fake/repo.git",
        os.path.join("data/repos", "repo")
    )

def test_parse_python_functions(sample_repo_path):
    """测试Python函数解析"""
    parser = CodeParser()
    sample_file = os.path.join(sample_repo_path, "sample.py")
    
    # 示例文件内容：
    # def add(a, b):
    #     return a + b
    # class Test:
    #     def method(self):
    #         pass
    
    blocks = parser._parse_python(sample_file)
    print(blocks)
    assert len(blocks) == 3
    assert blocks[0]["name"] == "add"
    assert blocks[1]["name"] == "method"
    assert "return a + b" in blocks[0]["code"]