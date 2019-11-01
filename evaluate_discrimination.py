#!/usr/bin/env python
"""This script evaluates the discriminative task: each candidate model applies
a probability to candidate continuations for a given primer. The higher the
probability given to the true continuation, and lower the probability given to
the false continuation(s), the better the score. In the 2019 competition, only
two continuations are scored, but this script is written in such a way that we
could accept an arbitrary number of false continuation scores.

The input data files are expected to be of the format:
    id,A,B,...,Z
    01234abcd,0.00092,0.001,...,0.9
    12345bcd3,0.092,0.01,...,0.7
    ...

Where id represents the identity of the exerpt being evaluated, the final
column is the true continuation score, and all other columns are false
continuation scores.

N.B. It is assumed that the rows sum to 1, with the values representing the
probability of each excerpt being the true continuation.
"""
import os.path as op

import numpy as np
import pandas as pd

import config



SMALLEST_NUMBER = np.finfo(float).eps



def softmax(x, axis=-1):
    """Returns the softmax for each row of the input x. For numerical
    stability, we subtract the maximum value from each row first before getting
    the exponents.
    """
    exp = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp / np.sum(exp, axis=axis, keepdims=True)


def negloglike(x, labels):
    """Returns the negative log likelihood from each row of x (unnormalized
    probabilities - we apply a softmax to each row first).
    """
    # TODO: note that it is assumed every row has already been normalized
#    probs = softmax(x)
    probs = x
    # select only the prob of true lab
    return -np.log(probs[:, labels] + SMALLEST_NUMBER)
    

def get_scores(x, labels=None):
    """Returns the required scores: accuracy, mean negative log likelihood (the
    crossentropy), and the variance of the negative log likelihood. If labels
    is not supplied (a list of indices indicating the true label for each row),
    it is assumed the final column of each row is the true label (this is very
    specific to our particular expected input!)"""
    nr_obs = x.shape[0]
    nr_cols = x.shape[1]
    max_idx = nr_cols - 1
    if labels is None:
        labels = max_idx * np.ones(nr_obs, dtype=int)
    accuracy = np.mean(np.argmax(x, axis=-1) == labels)
    nll = negloglike(x, labels)
    crossent = np.mean(nll)
    # Renormalising and making 1 best and 0 worst
    worst_crossent = -np.log(SMALLEST_NUMBER)
    best_crossent = -np.log(1 + SMALLEST_NUMBER)
    # renormalise
    crossent_score = ((crossent - best_crossent) /
                      (worst_crossent - best_crossent))
    # reverse
    crossent_score = 1 - crossent_score
#    nll_var = np.var(nll)
    return nr_obs, accuracy, crossent_score


if __name__ == '__main__':
    paths = {
        'mono': config.DISCRIM_MONO_FILES,
        'poly': config.DISCRIM_POLY_FILES
    }
    
    # Score each file
    scores = pd.DataFrame(
        columns=['model', 'data', 'nr_obs', 'accuracy', 'crossentropy_score'],
        dtype=float
    )
    scores.nr_obs = scores.nr_obs.astype(int)
    scores.data = scores.data.astype(str)
    scores.model = scores.model.astype(str)
    scores.set_index(['model', 'data'], inplace=True)
    
    for data_type in list(paths.keys()):
        files = paths[data_type]
        for model_name, fn in files.items():
            df = pd.read_csv(fn)
            x = df.iloc[:, 1:].values
            assert np.allclose(np.sum(x, axis=1), np.ones(x.shape[0])), (
                f'Rows in {model_name} discrim file do not sum to one. '
                'It is expected each value represents the probability of the '
                'each excerpt being the true continuation so rows should sum '
                'to one.')
            scores.loc[(model_name, data_type), :] = get_scores(x)
    
    # TODO: Check files have same set of ids (warn if not)
    
    # Output table of results
    scores.round(decimals=3).to_html(op.join(config.OUTPUT_FOLDER,
                'discrim_table.html'))
    scores.round(decimals=3).to_latex(op.join(config.OUTPUT_FOLDER,
                'discrim_table.tex'))

    print(scores.round(decimals=3))