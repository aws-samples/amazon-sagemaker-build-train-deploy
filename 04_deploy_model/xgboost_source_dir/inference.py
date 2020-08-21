import os
import pickle as pkl
import json
import numpy as np
import xgboost as xgb

from sagemaker_containers.beta.framework import (
    content_types, encoders, env, modules, transformer, worker)

from sagemaker_xgboost_container import encoder as xgb_encoders

def input_fn(input_data, content_type):    
    if content_type == content_types.JSON:
        obj = json.loads(input_data)
        features = obj['instances'][0]['features']
        array = np.array(features).reshape((1, -1))
        return xgb.DMatrix(array)
    else:
        return xgb_encoders.decode(input_data, content_type)

def model_fn(model_dir):
    model_file = model_dir + '/model.bin'
    model = pkl.load(open(model_file, 'rb'))
    return model
