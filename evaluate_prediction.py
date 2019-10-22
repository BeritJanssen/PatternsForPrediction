#!/usr/bin/env python
"""Script to evaluate all contributions for MIREX Patterns for Prediction 2019.
See README.md for configuration instructions.

References
----------
https://www.music-ir.org/mirex/wiki/2019:Patterns_for_Prediction
"""
import re
from glob import glob

import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

import config
from pitch import score_pitch
from cs import score_cs


def dedup_and_preproc(df):
    """In order that CS works correctly, we need to ensure there are no
    duplicate points in (onset, pitch) space. Given that score do not use
    any other data than onset and pitch, we are safe to drop other columns
    """
    df = df[['onset', 'pitch']].drop_duplicates()
    return df


if __name__ == '__main__':
    PATH = config.DATASET_PATH
    # CSV column keys in dataset
    COLNAMES = ['onset', 'pitch', 'morph', 'dur', 'ch']

    def get_fn(path):
        """Get the filename of the csv file to evaluate"""
        return path.split('/')[-1].split('.')[0]

    print('Reading PPTD csv files')
    prime = {get_fn(path): pd.read_csv(path, names=COLNAMES)
             for path in tqdm(glob(f'{PATH}/prime_csv/*'))}
    cont_true = {get_fn(path): pd.read_csv(path, names=COLNAMES)
                 for path in tqdm(glob(f'{PATH}/cont_true_csv/*'))}
    # preprocessing to remove duplicates
    cont_true = {fn: dedup_and_preproc(df) for fn, df in cont_true.items()}
    fn_list = list(prime.keys())

    files_dict = {}
    alg_names = config.MODEL_DIRS.keys()
    for alg in alg_names:
        print(f'Reading {alg} output files')
        alg_cont = {
            get_fn(path): pd.read_csv(path, names=config.MODEL_KEYS[alg])
            for path in tqdm(glob(f'{config.MODEL_DIRS[alg]}/*.csv'))
        }
        # preprocessing to remove duplicates
        alg_cont = {fn: dedup_and_preproc(df) for fn, df in alg_cont.items()}
        files_dict[alg] = alg_cont

    score_pitch(fn_list, alg_names, files_dict, cont_true) 
    #score_cs(fn_list, alg_names, files_dict, cont_true, prime)
