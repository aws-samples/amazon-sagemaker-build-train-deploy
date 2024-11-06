import os
import shutil
import xgboost
import numpy as np
import pandas as pd

from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

def train(X_train, y_train, X_val, y_val,
          eta=0.1, 
          max_depth=3, 
          gamma=0.0,
          min_child_weight=1,
          verbosity=0,
          objective='binary:logistic',
          eval_metric='auc',
          num_boost_round=5, experiment_name="main_experiment", run_id="run-01"):

    import mlflow
    import pandas as pd

    # Enable autologging in MLflow
    mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_ARN'])    
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_id=run_id) as run:        
        with mlflow.start_run(run_name="Train", nested=True):    
            mlflow.autolog()
            print('Train features shape: {}'.format(X_train.shape))
            print('Train labels shape: {}'.format(y_train.shape))
            print('Validation features shape: {}'.format(X_val.shape))
            print('Validation labels shape: {}'.format(y_val.shape))
        
            # Creating DMatrix(es)
            dtrain = xgboost.DMatrix(X_train, label=y_train)
            dval = xgboost.DMatrix(X_val, label=y_val)
            watchlist = [(dtrain, "train"), (dval, "validation")]
        
            print('')
            print (f'===Starting training with max_depth {max_depth}===')
        
            param_dist = {
                "max_depth": max_depth,
                "eta": eta,
                "gamma": gamma,
                "min_child_weight": min_child_weight,
                "verbosity": verbosity,
                "objective": objective,
                "eval_metric": eval_metric
            }
            mlflow.log_dict(param_dist, "xgboost_params.json")
            xgb = xgboost.train(
                params=param_dist,
                dtrain=dtrain,
                evals=watchlist,
                num_boost_round=num_boost_round)
        
            predictions = xgb.predict(dval)
        
            print ("Metrics for validation set")
            print('')
            print (pd.crosstab(index=y_val, columns=np.round(predictions),
                               rownames=['Actuals'], colnames=['Predictions'], margins=True))
            print('')
        
            rounded_predict = np.round(predictions)
        
            val_accuracy = accuracy_score(y_val, rounded_predict)
            val_precision = precision_score(y_val, rounded_predict)
            val_recall = recall_score(y_val, rounded_predict)
        
            print("Accuracy Model A: %.2f%%" % (val_accuracy * 100.0))
            print("Precision Model A: %.2f" % (val_precision))
            print("Recall Model A: %.2f" % (val_recall))
        
            val_auc = roc_auc_score(y_val, predictions)
            print("Validation AUC A: %.2f" % (val_auc))
        
            model_file_path="/opt/ml/model/xgboost_model.bin"
            os.makedirs(os.path.dirname(model_file_path), exist_ok=True)
            xgb.save_model(model_file_path)

    return xgb
