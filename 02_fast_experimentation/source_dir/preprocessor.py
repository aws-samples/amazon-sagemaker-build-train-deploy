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

from sagemaker.session import Session
from sagemaker.experiments import load_run

import boto3

from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

columns = ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Machine failure']
cat_columns = ['Type']
num_columns = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
target_column = 'Machine failure'

training_ratio = 0.8
validation_ratio = 0.1
test_ratio = 0.1
    

def save_dataframe_to_file(output_path, fileName, df):
    if not os.path.exists(output_path):
            os.makedirs(output_path)
    path = os.path.join(output_path, fileName)
    
    print('Saving to {}'.format(path))
    pd.DataFrame(df).to_csv(path, header=False, index=False)
    
    return path


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--input-data-path')
    parser.add_argument('--output-data-dir')
    parser.add_argument('--featurizer-model-dir')
    parser.add_argument('--s3-bucket-name')
    parser.add_argument('--s3-key-prefix')

    return parser.parse_known_args()


if __name__=='__main__':
    
    args, _ = parse_args()

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

    print(f'Splitting data training ({training_ratio}), validation ({validation_ratio}), and test ({test_ratio}) sets ')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_ratio, random_state=0, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=validation_ratio/(validation_ratio+training_ratio), random_state=2, stratify=y_train)
    
    #Apply transformations
    transformer = ColumnTransformer(transformers=[('numeric', StandardScaler(), num_columns),
                                                    ('categorical', OneHotEncoder(), cat_columns)],
                                    remainder='passthrough')
    featurizer_model = transformer.fit(X_train)
    X_train = featurizer_model.transform(X_train)
    X_val = featurizer_model.transform(X_val)
    X_test = featurizer_model.transform(X_test)
    
    print(f'Shape of train features after preprocessing: {X_train.shape}')
    print(f'Shape of validation features after preprocessing: {X_val.shape}')
    print(f'Shape of test features after preprocessing: {X_test.shape}')
    
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
    
    boto_session = boto3.session.Session()
    sagemaker_session = Session(boto_session=boto_session)
    
    with load_run(sagemaker_session=sagemaker_session) as run:

        run.log_parameters(
        {
          'train': training_ratio,
          'validate': validation_ratio,
          'test': test_ratio
        })

        run.log_artifact(name="train_data", value=train_features_output_path, media_type="text/csv", is_output=True)
        run.log_artifact(name="val_data", value=val_features_output_path, media_type="text/csv", is_output=True)
        run.log_artifact(name="test_data", value=test_features_output_path, media_type="text/csv", is_output=True)
        run.log_artifact(name="featurizer_model", value=model_joblib_path, media_type="text/plain", is_output=True)

    
    s3 = boto3.client("s3")
    print(f'Uploading to s3 bucket "{s3_bucket_name}" prefix "{s3_key_prefix}"')
                
    train_data_key = f'{s3_key_prefix}/data/preprocessed/train/train_features.csv'
    s3.upload_file(train_features_output_path, s3_bucket_name, train_data_key)
            
    val_data_key = f'{s3_key_prefix}/data/preprocessed/val/val_features.csv'
    s3.upload_file(val_features_output_path, s3_bucket_name, val_data_key)
    
    test_data_key = f'{s3_key_prefix}/data/preprocessed/test/test_features.csv'
    s3.upload_file(test_features_output_path, s3_bucket_name, test_data_key)
            
    train_labels_key = f'{s3_key_prefix}/data/preprocessed/train/train_labels.csv'
    s3.upload_file(train_labels_output_path, s3_bucket_name, train_labels_key)

    val_labels_key = f'{s3_key_prefix}/data/preprocessed/val/val_labels_csv'
    s3.upload_file(val_labels_output_path, s3_bucket_name, val_labels_key)

    test_labels_key = f'{s3_key_prefix}/data/preprocessed/test/test_labels_csv'
    s3.upload_file(test_labels_output_path, s3_bucket_name, val_labels_key)