import argparse
from typing import Dict, Union

import numpy
import pickle

from kserve import (
    Model,
    ModelServer,
    model_server,
    InferInput,
    InferRequest,
    InferResponse,
    logging,
)
from kserve.model import PredictorProtocol, PredictorConfig


with open('scaler.pkl', 'rb') as handle:
    scaler = pickle.load(handle)


def scale(data):
    """scales the input data using the Sci-kit Learn StandardScaler
    Args:
        data: The input data to be scaled
    Returns:
        numpy.array: Returns the numpy array after the scaling
    """

    return scaler.transform(data)


class ScalingTransformer(Model):
    def __init__(
            self,
            name: str,
            predictor_host: str,
            predictor_protocol: str,
            predictor_use_ssl: bool,
    ):
        super().__init__(
            name, PredictorConfig(predictor_host, predictor_protocol, predictor_use_ssl)
        )
        self.ready = True

    def preprocess(
            self, payload: Union[Dict, InferRequest], headers: Dict[str, str] = None
    ) -> Union[Dict, InferRequest]:
        print("payload", payload)
        if isinstance(payload, InferRequest):
            print("isinstance is InferRequest")
            input_tensors = scale(payload.inputs[0].data)
        else:
            print("isinstance NOT InferRequest")
            headers["request-type"] = "v1"
            input_tensors = [
                scale(instance["data"])
                for instance in payload["instances"]
            ]
        input_tensors = numpy.asarray(input_tensors, dtype=numpy.float32)
        print(input_tensors.dtype, input_tensors.shape, input_tensors)
        infer_inputs = [
            InferInput(
                name="dense_input",
                datatype="FP32",
                shape=list(input_tensors.shape),
                data=input_tensors,
            )
        ]
        print(infer_inputs)
        infer_request = InferRequest(model_name=self.name, infer_inputs=infer_inputs)

        # Transform to KServe v1/v2 inference protocol
        if self.protocol == PredictorProtocol.REST_V1.value:
            inputs = [{"data": input_tensor.tolist()} for input_tensor in input_tensors]
            payload = {"instances": inputs}
            return payload
        else:
            return infer_request

    def postprocess(
            self, infer_response: Union[Dict, InferResponse], headers: Dict[str, str] = None
    ) -> Union[Dict, InferResponse]:
        if "request-type" in headers and headers["request-type"] == "v1":
            if self.protocol == PredictorProtocol.REST_V1.value:
                return infer_response
            else:
                # if predictor protocol is v2 but transformer uses v1
                return {"predictions": infer_response.outputs[0].as_numpy().tolist()}
        else:
            return infer_response


parser = argparse.ArgumentParser(parents=[model_server.parser])
args, _ = parser.parse_known_args()

if __name__ == "__main__":
    if args.configure_logging:
        logging.configure_logging(args.log_config_file)

    model = ScalingTransformer(
        args.model_name,
        predictor_host=args.predictor_host,
        predictor_protocol=args.predictor_protocol,
        predictor_use_ssl=args.predictor_use_ssl,
    )
    ModelServer().start([model])
