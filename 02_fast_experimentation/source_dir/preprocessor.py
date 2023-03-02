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

from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

columns = ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Machine failure']
cat_columns = ['Type']
num_columns = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
target_column = 'Machine failure'

def save_data_locally(output_path, fileName, df):
    if not os.path.exists(output_path):
            os.makedirs(output_path)
    path = os.path.join(output_path, fileName)
    
    print('Saving to {}'.format(path))
    pd.DataFrame(df).to_csv(path, header=False, index=False)
    
    return path


if __name__=='__main__':
    
    # Read the arguments passed to the script
    parser = argparse.ArgumentParser()
    parser.add_argument('--train-val-split-ratio', type=float, default=0.2)
    parser.add_argument('--file-path', type=Path)
    parser.add_argument('--output-path', type=Path)
    parser.add_argument('--model-path', type=Path)
    parser.add_argument('--s3-prefix')
    
    args, _ = parser.parse_known_args()

    split_ratio = args.train_val_split_ratio
    input_path = args.file_path
    model_dir = args.model_path
    output_path = args.output_path
    s3_prefix = args.s3_prefix
    
    print(input_path)
    
    # Read input data into a Pandas dataframe
    df = pd.read_csv(input_path, usecols=columns)
    X = df.drop(target_column, axis=1)
    y = df[target_column]


    # Split data set
    print('Splitting data into train and test sets with ratio {}'.format(split_ratio))
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, 
                                                      random_state=0, stratify=y)
    
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=split_ratio, 
                                                      random_state=2, stratify=y_train)

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
    print('Testing features shape after preprocessing: {}'.format(X_val.shape))
    
    print(output_path)
                                                                
    train_features_output_path = save_data_locally(output_path, 'train_features.csv', X_train)
    train_labels_output_path = save_data_locally(output_path, 'train_labels.csv', y_train)

    val_features_output_path = save_data_locally(output_path, 'val_features.csv', X_val)
    val_labels_output_path = save_data_locally(output_path, 'val_labels.csv', y_val)
                                                                
    test_features_output_path = save_data_locally(output_path, 'test_features.csv', X_test)
    train_labels_output_path = save_data_locally(output_path, 'test_labels.csv', y_test)
    
    
    # Saving model artifacts locally
    if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    model_joblib_path = '{}/model.joblib'.format(model_dir)
    model_output_path = '{}/model.tar.gz'.format(model_dir)

    joblib.dump(featurizer_model, model_joblib_path)
    tar = tarfile.open(model_output_path, "w:gz")
    tar.add(model_joblib_path, arcname="model.joblib")
    tar.close()
    
    # (Optional) Saving outputs to S3 for later use 
    if s3_prefix is not None:
        s3 = boto3.client("s3")
        print('Uploading to s3 at s3://{}/{}'.format(bucket_name,s3_prefix))
        
        train_data_key = '{0}/data/preprocessed/train/train_features.csv'.format(s3_prefix)
        s3.upload_file(train_features_output_path ,bucket_name, train_data_key)
        
        val_data_key = '{0}/data/preprocessed/val/val_features.csv'.format(s3_prefix)
        s3.upload_file(val_features_output_path ,bucket_name, val_data_key)
        
        train_labels_key = '{0}/data/preprocessed/train/train_labels.csv'.format(s3_prefix)
        s3.upload_file(train_labels_output_path ,bucket_name, train_labels_key)

        val_labels_key = '{0}/data/preprocessed/val/val_labels_csv'.format(s3_prefix)
        s3.upload_file(val_labels_output_path ,bucket_name, val_labels_key)
        
        train_labels_key = '{0}/data/preprocessed/test/test_labels.csv'.format(s3_prefix)
        s3.upload_file(train_labels_output_path ,bucket_name, train_labels_key)

        val_labels_key = '{0}/data/preprocessed/test/test_labels_csv'.format(s3_prefix)
        s3.upload_file(val_labels_output_path ,bucket_name, val_labels_key)
        