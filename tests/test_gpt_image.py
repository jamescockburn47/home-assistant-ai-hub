import importlib
import sys
import types
from pathlib import Path

import pytest

# Skip these tests entirely if the openai package isn't installed
pytest.importorskip("openai")


def _setup_module(monkeypatch, tmp_path):
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    monkeypatch.setenv("OPENAI_API_KEY", "test")

    class DummyChatCompletions:
        def create(self, *args, **kwargs):
            return types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="Monet"))]
            )

    class DummyImages:
        def generate(self, *args, **kwargs):
            return types.SimpleNamespace(
                data=[types.SimpleNamespace(url="http://example.com/img.png")]
            )

    class DummyOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = types.SimpleNamespace(completions=DummyChatCompletions())
            self.images = DummyImages()

    monkeypatch.setattr('openai.OpenAI', DummyOpenAI)

    module = importlib.import_module('daily_brain_boost_complete')
    monkeypatch.setattr(module, 'OUTDIR', tmp_path)
    monkeypatch.setattr(module, 'WWW_DIR', tmp_path)
    (tmp_path / "images").mkdir(exist_ok=True)
    tmp_path.mkdir(exist_ok=True)

    return module


def test_gpt_image_download_success(monkeypatch, tmp_path):
    module = _setup_module(monkeypatch, tmp_path)

    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            self.content = b'data'

    monkeypatch.setattr(module.requests, 'get', lambda *a, **k: DummyResponse())

    assert module.gpt_image('test prompt', 'test.png') is True
    assert any(tmp_path.glob('test_*'))


def test_gpt_image_download_failure(monkeypatch, tmp_path):
    module = _setup_module(monkeypatch, tmp_path)

    class DummyResponse:
        def __init__(self):
            self.status_code = 404
            self.content = b''

    monkeypatch.setattr(module.requests, 'get', lambda *a, **k: DummyResponse())

    assert module.gpt_image('test prompt', 'fail.png') is False
    assert not any(tmp_path.glob('fail_*'))
