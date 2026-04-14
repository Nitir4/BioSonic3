import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


@pytest.fixture
def predictor(monkeypatch,tmp_path):
    """Import actual loader code without requiring a Torch/audio installation."""
    fake_torch=SimpleNamespace(cuda=SimpleNamespace(is_available=lambda:False),nn=SimpleNamespace(Module=object))
    for name,module in [('torch',fake_torch),('librosa',SimpleNamespace()),('timm',SimpleNamespace()),('joblib',SimpleNamespace())]:
        monkeypatch.setitem(__import__('sys').modules,name,module)
    path=Path(__file__).resolve().parents[1]/'model/predictor.py'
    spec=importlib.util.spec_from_file_location('tested_predictor',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.WEIGHTS_DIR=str(tmp_path)
    module.CLASS_NAMES_PATH=str(tmp_path/'class_names.pkl')
    module.ID_TO_NAME_PATH=str(tmp_path/'id_to_name.pkl')
    Path(module.CLASS_NAMES_PATH).touch()
    (tmp_path/'fold0.pth').touch();(tmp_path/'fold1.pth').touch()
    module.joblib.load=lambda path:np.array(['a','b']) if Path(path).name=='class_names.pkl' else {}
    return module


def test_reload_does_not_duplicate_folds(predictor,monkeypatch):
    monkeypatch.setattr(predictor,'_load_single_fold',lambda path,count:object())
    assert predictor.load_model() and predictor.is_model_ready()
    assert predictor.load_model() and len(predictor.fold_models)==2


def test_failed_fold_cannot_publish_partial_or_stale_ensemble(predictor,monkeypatch):
    predictor.fold_models=[object()];predictor.class_names=['old']
    def load(path,count):
        if Path(path).name=='fold1.pth':raise RuntimeError('Checkpoint mismatch')
        return object()
    monkeypatch.setattr(predictor,'_load_single_fold',load)
    with pytest.raises(RuntimeError):predictor.load_model()
    assert not predictor.is_model_ready() and not predictor.fold_models


def test_missing_metadata_clears_old_ensemble(predictor):
    predictor.fold_models=[object()];predictor.class_names=['old']
    Path(predictor.CLASS_NAMES_PATH).unlink()
    assert predictor.load_model() is False and not predictor.is_model_ready()


def test_checkpoint_loading_requires_all_keys(predictor,monkeypatch):
    calls=[]
    net=SimpleNamespace(load_state_dict=lambda data,strict:calls.append(strict),to=lambda device:None,eval=lambda:None)
    monkeypatch.setattr(predictor,'BirdModel',lambda num_classes:net)
    predictor.torch.load=lambda path,**kwargs: {}
    assert predictor._load_single_fold('fold.pth',2) is net
    assert calls==[True]
