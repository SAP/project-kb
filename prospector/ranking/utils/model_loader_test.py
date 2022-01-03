import os

import pytest

from ranking.utils.model_loader import get_model_path, load_model, save_model

from ..config import MODELS_FOLDER

# from ..ranking import *


@pytest.fixture
def model_name():
    return "LR_15_components"


@pytest.fixture
def model_name_joblib():
    return "LR_15_components.joblib"


def test_get_model_path(model_name, model_name_joblib):
    assert get_model_path(model_name_joblib) == os.path.join(
        MODELS_FOLDER, model_name_joblib
    )
    assert get_model_path(model_name) == os.path.join(
        MODELS_FOLDER, "{}.joblib".format(model_name)
    )


def test_load_model(model_name, model_name_joblib):
    model1 = load_model(model_name)
    assert model1 is not None
    model2 = load_model(model_name_joblib)
    assert model2 is not None


def test_save_model(model_name):
    model = load_model(model_name)
    path = save_model(model, "test123")
    assert os.path.exists(path)

    # Cleaning the tested saved model
    if os.path.exists(path):
        os.remove(path)
