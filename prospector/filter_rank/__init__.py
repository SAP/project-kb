import os

cwd = os.path.dirname(__file__)
MODELS_FOLDER = os.path.join(cwd, "..", "models")
TRAINING_DATA = os.path.join(
    cwd, "data", "raw_data", "projectkb_dataset_20210415_sample.csv"
)
NUM_ELEMENTS_TRAINING_DATA = (
    6  # This is the number of elements in the training dataset file
)
