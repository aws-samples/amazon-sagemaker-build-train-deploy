import io
import os
import json
import s3fs
import joblib

import xgboost
import sklearn
import numpy as np
import pandas as pd

import boto3

import sagemaker
from sagemaker.pipeline import PipelineModel
from sagemaker import ModelMetrics, MetricsSource
from sagemaker.s3_utils import s3_path_join
from sagemaker.utils import unique_name_from_base
from sagemaker.image_uris import retrieve as get_image_uri

from sagemaker.serve import ModelServer
from sagemaker.serve import InferenceSpec
from sagemaker.serve.builder.model_builder import ModelBuilder
from sagemaker.serve.builder.schema_builder import SchemaBuilder
from sagemaker.serve import CustomPayloadTranslator

# AWS Region
session = boto3.session.Session()
current_region = session.region_name

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
        image_uri=get_image_uri(framework="sklearn", region=current_region, version="1.2-1"),
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

def register(role, featurizer_model, booster, 
             bucket_name, model_report_dict,
             model_package_group_name, model_approval_status):

    sklearn_model = build_sklearn_sagemaker_model(role, featurizer_model)
    xgboost_model = build_xgboost_sagemaker_model(role, booster)

    # Upload evaluation report to s3
    eval_file_name = unique_name_from_base("evaluation")
    eval_report_s3_uri = s3_path_join(
        "s3://",
        bucket_name,
        model_package_group_name,
        f"evaluation-report/{eval_file_name}.json",
    )
    
    s3_fs = s3fs.S3FileSystem()
    eval_report_str = json.dumps(model_report_dict)
    with s3_fs.open(eval_report_s3_uri, "wb") as file:
        file.write(eval_report_str.encode("utf-8"))
    
    # Create model_metrics as per evaluation report in Amazon S3
    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri=eval_report_s3_uri,
            content_type="application/json",
        )
    )

    pipeline_model_name = unique_name_from_base("sagemaker-btd-pipeline-model")
    pipeline_model = PipelineModel(
        name=pipeline_model_name,
        sagemaker_session=xgboost_model.sagemaker_session,
        role=role,
        models=[
            sklearn_model, 
            xgboost_model])

    pipeline_model.register(
        content_types=["text/csv"],
        response_types=["application/x-npy"],
        model_package_group_name=model_package_group_name,
        approval_status=model_approval_status,
        model_metrics=model_metrics)

    sagemaker_client = boto3.client("sagemaker")
    
    response = sagemaker_client.list_model_packages(
        MaxResults=100,
        ModelPackageGroupName=model_package_group_name,
        ModelPackageType='Versioned',
        SortBy='CreationTime',
        SortOrder='Descending'
    )

    model_package_arn = response["ModelPackageSummaryList"][0]["ModelPackageArn"]

    print(f"Successfully registered model package {model_package_arn}.")

    return model_package_arn
