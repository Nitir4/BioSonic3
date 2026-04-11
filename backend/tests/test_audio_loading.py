import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
import pytest


@pytest.fixture
def audio_loader(monkeypatch):
    decoder = SimpleNamespace()
    monkeypatch.setitem(sys.modules, 'librosa', decoder)
    path = Path(__file__).resolve().parents[1] / 'processing/audio_loader.py'
    spec = importlib.util.spec_from_file_location('tested_audio_loader', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, decoder


def test_valid_audio_is_preserved(audio_loader):
    module, decoder = audio_loader
    samples = np.array([0., .5, -.5])
    decoder.load = lambda path, sr: (samples, 32000)
    result, rate = module.load_audio('upload.wav')
    np.testing.assert_array_equal(result, samples)
    assert rate == 32000


def test_decoder_failure_is_an_invalid_upload(audio_loader):
    module, decoder = audio_loader
    def fail(path, sr):
        raise RuntimeError('unsupported encoding')
    decoder.load = fail
    with pytest.raises(ValueError, match='decoded'):
        module.load_audio('upload.wav')


@pytest.mark.parametrize('samples,rate', [([], 32000), ([np.nan], 32000), ([0.], 0)])
def test_invalid_samples_are_rejected(audio_loader, samples, rate):
    module, decoder = audio_loader
    decoder.load = lambda path, sr: (np.asarray(samples), rate)
    with pytest.raises(ValueError, match='valid audio samples'):
        module.load_audio('upload.wav')
