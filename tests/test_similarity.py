import pytest
from src.similarity import SimilarityCalculator

@pytest.fixture
def similarity_calculator():
    return SimilarityCalculator()

def test_text_similarity_calculation(similarity_calculator):
    """测试文本相似度计算"""
    query = {"normalized_code": "def func(VAR): return VAR + 1"}
    candidate = {
        "metadata": {"normalized_code": "def func(VAR): return VAR + 2"},
        "distance": 0.5
    }
    
    result = similarity_calculator.calculate_similarity(query, [candidate])
    assert 0.7 < result[0]["similarity"] < 1  # 预期高相似度但非完全匹配

def test_zero_similarity_edge_case(similarity_calculator):
    """测试完全不同的代码返回低相似度"""
    query = {"normalized_code": "print('hello')"}
    candidate = {
        "metadata": {"normalized_code": "for VAR in range(10): pass"},
        "distance": 9
    }
    
    result = similarity_calculator.calculate_similarity(query, [candidate])
    assert result[0]["similarity"] < 0.3