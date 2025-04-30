import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.estimate_translation_cost import estimate_token_count_precise

def test_estimate_token_count_precise_basic():
    input_lines = ["Hello world", "This is a test sentence."]
    model = "gpt-4-turbo"
    input_tokens, output_tokens = estimate_token_count_precise(input_lines, model)

    assert input_tokens > 0
    assert output_tokens > 0
    assert isinstance(input_tokens, int)
    assert isinstance(output_tokens, int)

from scripts.estimate_translation_cost import calculate_cost

def test_calculate_cost_gpt4turbo_basic():
    input_tokens = 1000
    output_tokens = 500
    model = "gpt-4-turbo"
    result = calculate_cost(input_tokens, output_tokens, model)
    assert isinstance(result, float)
    assert result == round((1000 * 0.01 + 500 * 0.03) / 1000, 4)

def test_calculate_cost_unknown_model():
    try:
        calculate_cost(100, 100, "unknown-model")
        assert False, "Exception not raised for unknown model"
    except ValueError as e:
        assert "Ismeretlen modell" in str(e)
