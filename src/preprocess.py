import logging
import os
import pathlib
import pickle
import glob
import warnings
from pathlib import Path
from joblib import Parallel, delayed
from tqdm import tqdm

import catboost as cb
import joblib
import lightgbm as lgb
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow.keras as keras
import xgboost as xgb
import consts
from sklearn.compose import *
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import *
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import *
from sklearn.pipeline import *
from sklearn.preprocessing import *
from sklearn.tree import *
from skimage.transform import resize

warnings.filterwarnings("ignore")

logging.basicConfig(
    format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO
)

SEED = 1121218


def resize_image(path, target_size=(224, 224), save_path="data/processed/train"):
    """A function to resize images."""
    img = plt.imread(path)
    img = resize(img, target_size)

    plt.imsave(save_path)

    return img


def execute_parallel(func, iterator):
    """A function to execute parallel jobs on the iterator."""
    Parallel(n_jobs=-1, backend="multiprocessing")(
        delayed(func)(item) for item in tqdm(iterator))


def save_tf_datasets():
    """A function to save images as TF datasets."""
    train_df = pd.read_csv("data/raw/train.csv")
    train_df['filename'] = 'data/raw/train/' + train_df['Id'] + '.jpg'

    img_size = (224, 224)
    rescale = 1.0 / 255.0

    data_generator = ImageDataGenerator(rescale=rescale, validation_split=0.2)
    gen_kwargs = dict(
        dataframe=train_df,
        directory="data/raw/train",
        x_col="filename",
        y_col="Pawpularity",
        batch_size=32,
        seed=SEED,
        shuffle=True,
        class_mode='raw',
        target_size=img_size,
    )

    train_generator = data_generator.flow_from_dataframe(**gen_kwargs, subset="training")
    validation_generator = data_generator.flow_from_dataframe(**gen_kwargs,
                                                              subset="validation")


if __name__ == "__main__":
    img_paths = glob.glob("data/raw/train/*.jpg")

    execute_parallel(resize_image, img_paths)
