Evaluation script to calculate precision, recall and F1-score of CSV representations of algorithmic continuations against the true continuations, using translation vectors.

To run: 
- 1. run `pip install -r requirements.txt`. 
- 2. Make a file ``config.py'' and define the following:
```python
# point the dataset path to the appropriate path on your file system
DATASET_PATH = "path/to/the/evaluation/set"
# model_dirs is a dictionary with the tested model as key,
# the directory as value
MODEL_DIRS = {
    'model1': 'path/to/model1/output',
    'model2': 'path/to/model2/output',
    'baseline': 'path/to/baseline/in/training/data'
}
# model_keys are lists of keys with which the generated csvs should be read
MODEL_KEYS = {
    'model1': ['onset', 'pitch'],
    'model2': ['onset', 'pitch', 'ioi', 'mnn'],
    'baseline': ['onset', 'pitch', 'morph', 'dur', 'ch']
}
```
- 3. Then run `python evaluate_prediction.py`. This will calculate the measures and render them as graphs. On Mac OS X, Matplotlib may still need to be configured, see [Matplotlib FAQ](https://matplotlib.org/faq/osx_framework.html). Code tested in Python 3.5.4.