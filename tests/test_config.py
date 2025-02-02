import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """测试环境初始化"""
    test_repo_path = Path(__file__).parent / "test_utils/sample_repo"
    test_data_path = Path("data/repos/sample_repo")
    
    # 复制测试仓库到临时目录
    if not test_data_path.exists():
        shutil.copytree(test_repo_path, test_data_path)
    
    yield
    
    # 测试后清理
    if test_data_path.exists():
        shutil.rmtree(test_data_path)