import io
import os
import sys
import json
import joblib
import subprocess

import xgboost
import sklearn
import numpy as np
import pandas as pd

import boto3

from sagemaker import get_execution_role
from sagemaker.s3 import S3Downloader
from sagemaker.pipeline import PipelineModel
from sagemaker import ModelMetrics, MetricsSource
from sagemaker.s3_utils import s3_path_join
from sagemaker.utils import unique_name_from_base
from sagemaker.image_uris import retrieve as get_image_uri
from sagemaker.deserializers import NumpyDeserializer
from sagemaker.predictor import Predictor

from sagemaker.serve import ModelServer
from sagemaker.serve import InferenceSpec
from sagemaker.serve.builder.model_builder import ModelBuilder
from sagemaker.serve.builder.schema_builder import SchemaBuilder
from sagemaker.serve import CustomPayloadTranslator

def get_model_artifacts_for_last_job(job_name_prefix):
    import boto3
    sagemaker_client = boto3.client('sagemaker')
    
    search_response = sagemaker_client.search(
        Resource='TrainingJob',
        SearchExpression={
            'Filters': [
                {
                    'Name': 'TrainingJobName',
                    'Operator': 'Contains',
                    'Value': job_name_prefix
                },
            ]
        },
        SortBy='CreationTime',
        SortOrder='Descending',
        MaxResults=1)
    
    return search_response['Results'][0]['TrainingJob']['ModelArtifacts']['S3ModelArtifacts']

def load_models(sklearn_job_prefix, xgboost_job_prefix):
    subprocess.call(['rm', '-rf', 'sklearn_model/'])
    subprocess.call(['rm', '-rf', 'xgboost_model/'])
    
    sklearn_s3_model_artifacts = get_model_artifacts_for_last_job(sklearn_job_prefix)
    print(f"SKLearn S3 model artifacts: {sklearn_s3_model_artifacts}")
    xgboost_s3_model_artifacts = get_model_artifacts_for_last_job(xgboost_job_prefix)
    print(f"XGBoost S3 model artifacts: {xgboost_s3_model_artifacts}")

    print(S3Downloader.download(sklearn_s3_model_artifacts, "sklearn_model/"))
    print(S3Downloader.download(xgboost_s3_model_artifacts, "xgboost_model/"))

    subprocess.call(['tar', '-xvzf', 'sklearn_model/model.tar.gz', '-C', 'sklearn_model/'])
    subprocess.call(['rm', 'sklearn_model/model.tar.gz'])
    subprocess.call(['tar', '-xvzf', 'xgboost_model/model.tar.gz', '-C', 'xgboost_model/'])
    subprocess.call(['rm', 'xgboost_model/model.tar.gz'])

    featurizer = joblib.load('sklearn_model/sklearn_model.joblib')
    booster = xgboost.Booster()
    booster.load_model('xgboost_model/xgboost_model.bin')

    return featurizer, booster

def build_sklearn_sagemaker_model(role, featurizer):
    feature_columns_names = ['Type', 'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
    
    class SklearnRequestTranslator(CustomPayloadTranslator):
        # This function converts the payload to bytes - happens on client side
        def serialize_payload_to_bytes(self, payload: object) -> bytes:
            return payload.encode("utf-8");
            
        # This function converts the bytes to payload - happens on server side
        def deserialize_payload_from_stream(self, stream) -> pd.DataFrame:
            df = pd.read_csv(io.BytesIO(stream.read()), header=None)
            df.columns = feature_columns_names
            return df
    
    class SklearnModelSpec(InferenceSpec):
        def invoke(self, input_object: object, model: object):       
            features = model.transform(input_object)
            return features
    
        def load(self, model_dir: str):
            model_path = model_dir+'/sklearn_model.joblib'
            print(model_path)
            model = joblib.load(model_path)
            return model
    
    schema_builder=SchemaBuilder(
        sample_input="L,298.4,308.2,1582,70.7,216",
        sample_output=np.array([0.647088,0.467287,-0.191472,0.720195,-0.536976,0.0,1.0,0.0]),
        input_translator=SklearnRequestTranslator()
    )

    model_file_path="sklearn_model/sklearn_model.joblib"
    os.makedirs(os.path.dirname(model_file_path), exist_ok=True)
    joblib.dump(featurizer, model_file_path)

    model_builder = ModelBuilder(
        model_path="sklearn_model/",
        name="sklearn_featurizer",
        dependencies={"requirements": "requirements_inference.txt"},
        image_uri=get_image_uri(framework="sklearn", region="us-west-2", version="1.2-1"),
        schema_builder=schema_builder,
        model_server=ModelServer.TORCHSERVE,
        inference_spec=SklearnModelSpec(),
        role_arn=role)
    
    return model_builder.build()

def build_xgboost_sagemaker_model(role, booster):

    class RequestTranslator(CustomPayloadTranslator):
        # This function converts the payload to bytes - happens on client side
        def serialize_payload_to_bytes(self, payload: object) -> bytes:
            return self._convert_numpy_to_bytes(payload)
            
        # This function converts the bytes to payload - happens on server side
        def deserialize_payload_from_stream(self, stream) -> xgboost.DMatrix:
            np_array = np.load(io.BytesIO(stream.read())).reshape((1, -1))
            dmatrix = xgboost.DMatrix(np_array)
            return dmatrix
            
        def _convert_numpy_to_bytes(self, np_array: np.ndarray) -> bytes:
            buffer = io.BytesIO()
            np.save(buffer, np_array)
            return buffer.getvalue()

    schema_builder=SchemaBuilder(
        sample_input=np.array([0.647088,0.467287,-0.191472,0.720195,-0.536976,0.0,1.0,0.0]),
        sample_output=np.array([0.15388985]),
        input_translator=RequestTranslator()
    )

    model_file_path = 'xgboost_model/xgboost_model.bin'
    os.makedirs(os.path.dirname(model_file_path), exist_ok=True)
    booster.save_model(model_file_path)

    model_builder = ModelBuilder(
        model=booster,
        model_path="xgboost_model/",
        dependencies={"requirements": "requirements_inference.txt"},
        schema_builder=schema_builder,
        role_arn=role)
    
    return model_builder.build()

def build_pipeline_model(role, sklearn_model, xgboost_model):
    pipeline_model_name = unique_name_from_base("sagemaker-btd-pipeline-model")

    pipeline_model = PipelineModel(
        name=pipeline_model_name, 
        role=role,
        models=[
            sklearn_model, 
            xgboost_model])

    return pipeline_model

def deploy_model(pipeline_model, instance_type, wait):
    endpoint_name = unique_name_from_base("sagemaker-btd-endpoint")
    
    pipeline_model.deploy(initial_instance_count=1, 
                          instance_type=instance_type, 
                          endpoint_name=endpoint_name,
                          wait=wait)

def run_test_inferences(endpoint_name):
    from io import BytesIO
    
    predictor = Predictor(endpoint_name=endpoint_name)

    payload = "L,298.4,308.2,1582,70.7,216"
    buffer = predictor.predict(payload)
    np_bytes = BytesIO(buffer)
    print(f"Inference payload: {payload}")
    print(f"Inference result: {np.load(np_bytes, allow_pickle=True)}")

    payload = "M,298.4,308.2,1582,30.2,214"
    buffer = predictor.predict(payload)
    np_bytes = BytesIO(buffer)
    print(f"Inference payload: {payload}")
    print(f"Inference result: {np.load(np_bytes, allow_pickle=True)}")

if __name__ == "__main__":

    if len(sys.argv) > 2 and sys.argv[1] == "--run-inference":
        endpoint_name = sys.argv[2]
        run_test_inferences(endpoint_name)
    else:
        role=get_execution_role()
        print(role)

        sklearn_job_prefix = "amzn-sm-btd-preprocess"
        xgboost_job_prefix = "amzn-sm-btd-train"
    
        featurizer, booster = load_models(sklearn_job_prefix, xgboost_job_prefix)
        
        sklearn_model = build_sklearn_sagemaker_model(role, featurizer)
        xgboost_model = build_xgboost_sagemaker_model(role, booster)
    
        pipeline_model = build_pipeline_model(role, sklearn_model, xgboost_model)
    
        deploy_model(pipeline_model, "ml.m5.xlarge", wait=False)
