from filter_rank import MODELS_FOLDER

from joblib import load, dump
import os


def get_model_path(model_name: str) -> str:
    """
    A helper function to retrieve the model path
    """
    if model_name.endswith('.joblib'):
        return os.path.join(MODELS_FOLDER, model_name)
    else:
        return os.path.join(MODELS_FOLDER, '{}.joblib'.format(model_name))


def load_model(model_name: str):
    """
    Serves for loading existing pre-trained modules from disk. Takes string model name as an input (the name of the
    saved model - can be with or without file extension) and returns the loaded model.
    If the requested model is not found, the function returns "Model not found" exception.
    """
    model_path = get_model_path(model_name)

    if not os.path.exists(model_path):
        raise Exception('Model {} not found'.format(model_name))

    return load(model_path)


def save_model(model, model_name: str) -> str:
    """
    Serves for saving pre-trained models to disk. Takes <model, model_name> as input (the name of the
    saved model - can be with or without file extension).
    Raises Exception if the model cannot be saved to disk.
    """
    model_path = get_model_path(model_name)
    dump(model, model_path)
    return model_path
