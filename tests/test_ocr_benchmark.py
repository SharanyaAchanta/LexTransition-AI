import importlib.util
from pathlib import Path


def _load_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "ocr_benchmark.py"
    spec = importlib.util.spec_from_file_location("ocr_benchmark", str(module_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_metric_helpers():
    mod = _load_module()
    assert mod.levenshtein("abc", "abc") == 0
    assert mod.cer("abc", "abc") == 0.0
    assert mod.keyword_recall("legal notice section 420", "section 420 notice") > 0
