IMAGE_TAG ?= quay.io/cfchase/fraud-detection-transformer:latest

build:
	podman build --platform linux/amd64 -t ${IMAGE_TAG} -f Dockerfile .

push:
	podman push ${IMAGE_TAG}

run:
	podman run -ePORT=8080 -p8080:8080 ${IMAGE_TAG} "python model.py --model_name=fraud --predictor_protocol=v2 --predictor_host=${PREDICTOR_HOST} predictor_use_ssl=True"


run-local:
	python model.py --model_name=fraud --predictor_protocol=v2 --predictor_host=${PREDICTOR_HOST} predictor_use_ssl=True

deploy:
	oc process -p PREDICTOR_HOST=${PREDICTOR_HOST} -f templates/inference-service.yaml | oc apply -f -

undeploy:
	oc process -p PREDICTOR_HOST=${PREDICTOR_HOST} -f templates/inference-service.yaml | oc delete -f -

test-local:
	curl -k -H "Content-Type: application/json" http://localhost:8080/v2/models/fraud/infer -d @./scripts/v2_input.json

test-service-v2:
	curl -k -H "Content-Type: application/json" ${TRANSFORMER_URL}/v2/models/fraud/infer -d @./scripts/v2_input.json


