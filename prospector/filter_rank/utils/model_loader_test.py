import pytest

from filter_rank.utils.model_loader import load_model


@pytest.fixture
def model_name():
    return "LR_15_components"


@pytest.fixture
def model_name_joblib():
    return "LR_15_components.joblib"


def test_load_model(model_name, model_name_joblib):
    model1 = load_model(model_name)
    assert model1 is not None
    model2 = load_model(model_name_joblib)
    assert model2 is not None
