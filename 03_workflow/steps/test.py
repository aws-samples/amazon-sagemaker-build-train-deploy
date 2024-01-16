import pandas as pd
import numpy as np

import xgboost

from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

def test(featurizer_model, booster, X_test, y_test):

    X_test = featurizer_model.transform(X_test)
    y_test = y_test.values.reshape(-1)

    dtest = xgboost.DMatrix(X_test, label=y_test)
    test_predictions = booster.predict(dtest)
    
    print ("===Metrics for Test Set===")
    print('')
    print (pd.crosstab(index=y_test, columns=np.round(test_predictions), 
                                     rownames=['Actuals'], 
                                     colnames=['Predictions'], 
                                     margins=True))
    print('')

    rounded_predict = np.round(test_predictions)

    accuracy = accuracy_score(y_test, rounded_predict)
    precision = precision_score(y_test, rounded_predict)
    recall = recall_score(y_test, rounded_predict)
    print('')

    print("Accuracy Model A: %.2f%%" % (accuracy * 100.0))
    print("Precision Model A: %.2f" % (precision))
    print("Recall Model A: %.2f" % (recall))

    auc = roc_auc_score(y_test, test_predictions)
    print("AUC A: %.2f" % (auc))

    report_dict = {
        "binary_classification_metrics": {
            "recall": {"value": recall, "standard_deviation": ""},
            "precision": {"value": precision, "standard_deviation": ""},
            "accuracy": {"value": accuracy, "standard_deviation": ""},
            "auc": {"value": auc, "standard_deviation": ""},
        }
    }
    print(f"evaluation report: {report_dict}")

    return report_dict

