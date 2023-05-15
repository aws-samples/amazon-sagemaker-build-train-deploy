import argparse
import os
import pandas as pd
import numpy as np

import xgboost

from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

from sagemaker.session import Session
from sagemaker.experiments import load_run

def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--preprocessed-data-dir')
    parser.add_argument('--model-dir')
    parser.add_argument('--eta', default='0.1', type=float)
    parser.add_argument('--max-depth', default=3, type=int)
    parser.add_argument('--gamma', default='0.0', type=float)
    parser.add_argument('--min-child-weight', default='1', type=int)
    parser.add_argument('--verbosity', default='0', type=int)
    parser.add_argument('--objective', default='binary:logistic')
    parser.add_argument('--eval-metric', default='auc')
    parser.add_argument('--num-boost-round', default=5, type=int)

    return parser.parse_known_args()

if __name__=='__main__':

    args, _ = parse_args()

    print(f'Received arguments {args}')
    
    preprocessed_data_dir = args.preprocessed_data_dir
    model_dir = args.model_dir
    eta = args.eta
    max_depth = args.max_depth
    gamma = args.gamma
    min_child_weight = args.min_child_weight
    verbosity = args.verbosity
    objective = args.objective
    eval_metric = args.eval_metric
    num_boost_round = args.num_boost_round
    
    train_features_path = os.path.join(preprocessed_data_dir, 'train_features.csv')
    train_labels_path = os.path.join(preprocessed_data_dir, 'train_labels.csv')
    
    val_features_path = os.path.join(preprocessed_data_dir, 'val_features.csv')
    val_labels_path = os.path.join(preprocessed_data_dir, 'val_labels.csv')
    
    print('Loading training data...')
    df_train_features = pd.read_csv(train_features_path, header=None)
    df_train_labels = pd.read_csv(train_labels_path, header=None)
    
    print('Loading validation data...')
    df_val_features = pd.read_csv(val_features_path, header=None)
    df_val_labels = pd.read_csv(val_labels_path, header=None)

    train_X = df_train_features.values
    train_y = df_train_labels.values.reshape(-1)
    print('Train features shape: {}'.format(X.shape))
    print('Train labels shape: {}'.format(y.shape))
    
    val_X = df_val_features.values
    val_y = df_val_labels.values.reshape(-1)
    print('Validation features shape: {}'.format(val_X.shape))
    print('Validation labels shape: {}'.format(val_y.shape))

    dtrain = xgboost.DMatrix(train_X, label=train_y)
    dval = xgboost.DMatrix(val_X, label=val_y)
    watchlist = [(dtrain, "train"), (dval, "validation")]
       
    print('')
    print (f'===Starting training with max_depth {max_depth}===')

    with load_run(sagemaker_session=sagemaker_session) as run:

        param_dist = {
            "max_depth": max_depth,
            "eta": eta,
            "gamma": gamma,
            "min_child_weight": min_child_weight,
            "verbosity": verbosity,
            "objective": objective,
            "eval_metric": eval_metric
        }
        
        run.log_parameters(param_dist)
            
        xgb = xgboost.train(
            params=param_dist,
            dtrain=dtrain,
            evals=watchlist,
            num_boost_round=num_boost_round)

        print('Training complete. Saving model...')
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        model_name = 'xgboost_model_{}.model'.format(str(int(time.time())))
        model_key = 'xgboost_model{}.joblib'.format(str(int(time.time())))
        model_path = os.path.join(model_dir, model_name)
        model_joblib_path = os.path.join(model_dir, model_key)
        xgb.save_model(model_path)
        xgb.save_model(model_joblib_path)

        predictions = xgb.predict(dval)
        print ("Metrics for validation set")
        print('')
        print (pd.crosstab(index=val_y, columns=np.round(predictions), rownames=['Actuals'], colnames=['Predictions'], margins=True))
        print('')
                
        rounded_predict = np.round(predictions)
        
        val_accuracy = accuracy_score(val_y, rounded_predict)
        val_precision = precision_score(val_y, rounded_predict)
        val_recall = recall_score(val_y, rounded_predict)

        print("Accuracy Model A: %.2f%%" % (val_accuracy * 100.0))
        print("Precision Model A: %.2f" % (val_precision))
        print("Recall Model A: %.2f" % (1 - val_recall))

        from sklearn.metrics import roc_auc_score

        val_auc = roc_auc_score(val_y, predictions)
        print("Validation AUC A: %.2f" % (val_auc))

        boto_session = boto3.session.Session()
        sagemaker_session = Session(boto_session=boto_session)    

        run.log_artifact(name="model", value=model_joblib_path, media_type="text/plain", is_output=True)
        run.log_metric(name="val_auc", value = val_auc)
        run.log_metric(name="val_accuracy", value = val_accuracy)
        run.log_metric(name="val_precision", value = val_precision)
        run.log_metric(name="val_recall", value = val_recall)

    