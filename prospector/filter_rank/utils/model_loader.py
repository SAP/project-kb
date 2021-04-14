from filter_rank import MODELS_FOLDER

from joblib import load
import os


def load_model(model_name: str):
    """
    Serves for loading existing pre-trained modules from disk. Takes string model name as an input (the name of the
    saved model - can be with or without file extension) and returns the loaded model.
    If the requested model is not found, the function returns "Model not found" exception.
    """
    if model_name.endswith('.joblib'):
        model_path = os.path.join(MODELS_FOLDER, model_name)
    else:
        model_path = os.path.join(MODELS_FOLDER, '{}.joblib'.format(model_name))

    if not os.path.exists(model_path):
        raise Exception('Model {} not found'.format(model_name))

    return load(model_path)
