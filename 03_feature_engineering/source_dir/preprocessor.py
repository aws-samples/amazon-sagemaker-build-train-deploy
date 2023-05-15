import argparse
import os
import warnings

import pandas as pd
import numpy as np
import tarfile

import boto3

from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

from sklearn.exceptions import DataConversionWarning

warnings.filterwarnings(action='ignore', category=DataConversionWarning)

columns = ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Machine failure']
cat_columns = ['Type']
num_columns = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
target_column = 'Machine failure'


def parse_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-test-split-ratio', type=float, default=0.3)
    args, _ = parser.parse_known_args()
    return args    


if __name__=='__main__':
          
    args = parse_args()

    print('Received arguments {}'.format(args))

    train_ratio = (1 - args.train_test_split_ratio)
    val_ratio = test_ratio = args.train_test_split_ratio / 2

    # Read input data into a Pandas dataframe.
    input_data_path = os.path.join('/opt/ml/processing/input', 'predictive_maintenance_raw_data_header.csv')
    print('Reading input data from {}'.format(input_data_path))
    df = pd.read_csv(input_data_path, usecols=columns)
    
    X = df.drop(target_column, axis=1)
    y = df[target_column]
    
    print(f'Splitting data training ({train_ratio}), validation ({val_ratio}), and test ({test_ratio}) sets ')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_ratio, random_state=0, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=val_ratio/(val_ratio+train_ratio), random_state=2, stratify=y_train)
        
    transformer = ColumnTransformer(transformers=[('numeric', StandardScaler(), num_columns),
                                                  ('categorical', OneHotEncoder(), cat_columns)],
                                    remainder='passthrough')
    
    featurizer_model = transformer.fit(X_train)
    X_train = featurizer_model.transform(X_train)
    X_val = featurizer_model.transform(X_val)
    X_test = featurizer_model.transform(X_test)
    
    print(f'Shape of training features after preprocessing: {X_train.shape}')
    print(f'Shape of training labels after preprocessing: {y_train.shape}')
    print(f'Shape of validation features after preprocessing: {X_val.shape}')
    print(f'Shape of validation labels after preprocessing: {y_val.shape}')
    print(f'Shape of test features after preprocessing: {X_test.shape}')
    print(f'Shape of test labels after preprocessing: {y_test.shape}')
    
    # Save outputs
    train_features_output_path = os.path.join('/opt/ml/processing/train', 'train_features.csv')
    train_labels_output_path = os.path.join('/opt/ml/processing/train', 'train_labels.csv')
    
    val_features_output_path = os.path.join('/opt/ml/processing/val', 'val_features.csv')
    val_labels_output_path = os.path.join('/opt/ml/processing/val', 'val_labels.csv')

    test_features_output_path = os.path.join('/opt/ml/processing/test', 'test_features.csv')
    test_labels_output_path = os.path.join('/opt/ml/processing/test', 'test_labels.csv')
    
    print(f'Saving training features to {train_features_output_path}')
    pd.DataFrame(X_train).to_csv(train_features_output_path, header=False, index=False)
    
    print(f'Saving validation features to {val_features_output_path}')
    pd.DataFrame(X_val).to_csv(val_features_output_path, header=False, index=False)
    
    print(f'Saving test features to {test_features_output_path}')
    pd.DataFrame(X_test).to_csv(test_features_output_path, header=False, index=False)    
    
    print(f'Saving training labels to {train_labels_output_path}')
    pd.DataFrame(y_train).to_csv(train_labels_output_path, header=False, index=False)
    
    print(f'Saving validation labels to {val_labels_output_path}')
    pd.DataFrame(y_val).to_csv(val_labels_output_path, header=False, index=False)
    
    print(f'Saving test labels to {test_labels_output_path}')
    pd.DataFrame(y_test).to_csv(test_labels_output_path, header=False, index=False)    
    
    # Save the model
    model_path = os.path.join('/opt/ml/processing/model', 'model.joblib')
    model_output_path = os.path.join('/opt/ml/processing/model', 'model.tar.gz')
    
    print('Saving featurizer model to {}'.format(model_output_path))
    joblib.dump(featurizer_model, model_path)
    tar = tarfile.open(model_output_path, "w:gz")
    tar.add(model_path, arcname="model.joblib")
    tar.close()
    
