from sagemaker.predictor import Predictor
import sys
import numpy as np

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
    if len(sys.argv) == 2:
        endpoint_name = sys.argv[1]
        run_test_inferences(endpoint_name)
    else:
        print('ERROR: Expected endpoint name as an argument')
        exit(1)