import pytest
from src.preprocessor import CodePreprocessor

@pytest.fixture
def preprocessor():
    return CodePreprocessor()

def test_process_removes_comments(preprocessor):
    code_block = {
        "file": "test.py",
        "code": "print('Hello') # This is a comment"
    }
    result = preprocessor.process(code_block)
    assert result["normalized_code"] == "print('VAR')"

def test_process_merges_whitespace(preprocessor):
    code_block = {
        "file": "test.py",
        "code": "print(   'Hello'   )"
    }
    result = preprocessor.process(code_block)
    assert result["normalized_code"] == "print( 'VAR' )"

def test_process_replaces_variable_names(preprocessor):
    code_block = {
        "file": "test.py",
        "code": "variable = 10"
    }
    result = preprocessor.process(code_block)
    assert result["normalized_code"] == "VAR = 10"

def test_process_handles_empty_code(preprocessor):
    code_block = {
        "file": "test.py",
        "code": ""
    }
    result = preprocessor.process(code_block)
    assert result["normalized_code"] == ""
