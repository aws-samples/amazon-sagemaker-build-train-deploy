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
    parser.add_argument('--input-data-path')
    parser.add_argument('--output-data-dir')
    parser.add_argument('--featurizer-model-dir')
    parser.add_argument('--s3-bucket-name')
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
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=train_val_split_ratio, random_state=2, stratify=y_train)
    
    #Apply transformations
    transformer = ColumnTransformer(transformers=[('numeric', StandardScaler(), num_columns),
                                                    ('categorical', OneHotEncoder(), cat_columns)],
                                    remainder='passthrough')
    featurizer_model = transformer.fit(X_train)
    X_train = featurizer_model.transform(X_train)
    X_val = featurizer_model.transform(X_val)
    X_test = featurizer_model.transform(X_test)
    
    print('Train features shape after preprocessing: {}'.format(X_train.shape))
    print('Validation features shape after preprocessing: {}'.format(X_val.shape))
    
    print(f'Output dir is {output_data_dir}')
                                                                
    train_features_output_path = save_dataframe_to_file(output_data_dir, 'train_features.csv', X_train)
    train_labels_output_path = save_dataframe_to_file(output_data_dir, 'train_labels.csv', y_train)

    val_features_output_path = save_dataframe_to_file(output_data_dir, 'val_features.csv', X_val)
    val_labels_output_path = save_dataframe_to_file(output_data_dir, 'val_labels.csv', y_val)
    
    test_features_output_path = save_dataframe_to_file(output_data_dir, 'test_features.csv', X_test)
    test_labels_output_path = save_dataframe_to_file(output_data_dir, 'test_labels.csv', y_test)
                                                                
    # Saving model artifacts
    if not os.path.exists(featurizer_model_dir):
            os.makedirs(featurizer_model_dir)
    model_joblib_path = f'{featurizer_model_dir}/model.joblib'
    model_output_path = f'{featurizer_model_dir}/model.tar.gz'

    print(f'Featurizer Model dir is {featurizer_model_dir}')
    joblib.dump(featurizer_model, model_joblib_path)
    tar = tarfile.open(model_output_path, "w:gz")
    tar.add(model_joblib_path, arcname="model.joblib")
    tar.close()
    
    s3 = boto3.client("s3")
    print(f'Uploading to s3 bucket "{s3_bucket_name}" prefix "{s3_key_prefix}"')
                
    train_data_key = f'{s3_key_prefix}/data/preprocessed/train/train_features.csv'
    s3.upload_file(train_features_output_path, s3_bucket_name, train_data_key)
            
    val_data_key = f'{s3_key_prefix}/data/preprocessed/val/val_features.csv'
    s3.upload_file(val_features_output_path, s3_bucket_name, val_data_key)
    
    test_data_key = f'{s3_key_prefix}/data/preprocessed/test/test_features.csv'
    s3.upload_file(train_labels_output_path, s3_bucket_name, test_data_key)
            
    train_labels_key = f'{s3_key_prefix}/data/preprocessed/train/train_labels.csv'
    s3.upload_file(train_labels_output_path, s3_bucket_name, train_labels_key)

    val_labels_key = f'{s3_key_prefix}/data/preprocessed/val/val_labels_csv'
    s3.upload_file(val_labels_output_path, s3_bucket_name, val_labels_key)

    test_labels_key = f'{s3_key_prefix}/data/preprocessed/test/test_labels_csv'
    s3.upload_file(val_labels_output_path, s3_bucket_name, val_labels_key)