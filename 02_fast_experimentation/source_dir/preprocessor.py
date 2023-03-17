import argparse
import os
import warnings

import pandas as pd
import tarfile
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

import boto3

from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

columns = ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Machine failure']
cat_columns = ['Type']
num_columns = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
target_column = 'Machine failure'

def save_dataframe_to_file(output_path, fileName, df):
    if not os.path.exists(output_path):
            os.makedirs(output_path)
    path = os.path.join(output_path, fileName)
    
    print('Saving to {}'.format(path))
    pd.DataFrame(df).to_csv(path, header=False, index=False)
    
    return path


if __name__=='__main__':
    
    # Read the arguments passed to the script
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-val-split-ratio', type=float)
    parser.add_argument('--input-data-path', type=Path)
    parser.add_argument('--output-data-dir', type=Path)
    parser.add_argument('--featurizer-model-dir', type=Path)
    parser.add_argument('--s3-bucket-name', type=Path)
    parser.add_argument('--s3-key-prefix')
    
    args, _ = parser.parse_known_args()

    train_val_split_ratio = args.train_val_split_ratio
    input_data_path = args.input_data_path
    output_data_dir = args.output_data_dir
    featurizer_model_dir = args.featurizer_model_dir
    s3_bucket_name = args.s3_bucket_name
    s3_key_prefix = args.s3_key_prefix
    
    print(f'Input path is {input_data_path}')
    
    # Read input data into a Pandas dataframe
    df = pd.read_csv(input_data_path, usecols=columns)
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    # Split data set
    print('Splitting data into train and test sets with ratio {}'.format(train_val_split_ratio))
    
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=train_val_split_ratio, random_state=0, stratify=y)

    #Apply transformations
    transformer = ColumnTransformer(transformers=[('numeric', StandardScaler(), num_columns),
                                                    ('categorical', OneHotEncoder(), cat_columns)],
                                    remainder='passthrough')
    featurizer_model = transformer.fit(X_train)
    X_train = featurizer_model.transform(X_train)
    X_val = featurizer_model.transform(X_val)
    
    print('Train features shape after preprocessing: {}'.format(X_train.shape))
    print('Validation features shape after preprocessing: {}'.format(X_val.shape))
    
    print(f'Output path is {output_data_dir}')
                                                                
    train_features_output_path = save_dataframe_to_file(output_data_dir, 'train_features.csv', X_train)
    train_labels_output_path = save_dataframe_to_file(output_data_dir, 'train_labels.csv', y_train)

    val_features_output_path = save_dataframe_to_file(output_data_dir, 'val_features.csv', X_val)
    val_labels_output_path = save_dataframe_to_file(output_data_dir, 'val_labels.csv', y_val)
                                                                
    # Saving model artifacts
    if not os.path.exists(featurizer_model_dir):
            os.makedirs(featurizer_model_dir)
    model_joblib_path = '{}/model.joblib'.format(featurizer_model_dir)
    model_output_path = '{}/model.tar.gz'.format(featurizer_model_dir)

    print(f'Featurizer Model path is {featurizer_model_dir}')
    joblib.dump(featurizer_model, model_joblib_path)
    tar = tarfile.open(model_output_path, "w:gz")
    tar.add(model_joblib_path, arcname="model.joblib")
    tar.close()
    
    s3 = boto3.client("s3")
    print(f'Uploading to s3://{s3_bucket_name}/{s3_key_prefix}')
                
    train_data_key = f'{s3_key_prefix}/data/preprocessed/train/train_features.csv'
    s3.upload_file(train_features_output_path, s3_bucket_name, train_data_key)
            
    val_data_key = f'{s3_key_prefix}/data/preprocessed/val/val_features.csv'
    s3.upload_file(val_features_output_path, s3_bucket_name, val_data_key)
            
    train_labels_key = f'{s3_key_prefix}/data/preprocessed/train/train_labels.csv'
    s3.upload_file(train_labels_output_path, s3_bucket_name, train_labels_key)

    val_labels_key = f'{s3_key_prefix}/data/preprocessed/val/val_labels_csv'
    s3.upload_file(val_labels_output_path, s3_bucket_name, val_labels_key)