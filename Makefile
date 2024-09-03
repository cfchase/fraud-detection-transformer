

build:
	podman build -t quay.io/cfchase/fraud-detection-transformer:latest -f Dockerfile .

push:
	podman push quay.io/cfchase/fraud-detection-transformer:latest

run:
	podman run -ePORT=8080 -p8080:8080 quay.io/cfchase/fraud-detection-transformer:latest "python model.py --model_name=fraud --predictor_protocol=v2 --predictor_host=fraud2-chase-kserve-raw.apps.dev.rhoai.rh-aiservices-bu.com predictor_use_ssl=True"


run-local:
	python model.py --model_name=fraud --predictor_protocol=v2 --predictor_host=fraud2-chase-kserve-raw.apps.dev.rhoai.rh-aiservices-bu.com predictor_use_ssl=True

deploy:
	oc apply -f templates/inference-service.yaml

undeploy:
	oc delete -f templates/inference-service.yaml

test-local:
	curl -k -H "Content-Type: application/json" http://localhost:8080/v2/models/fraud/infer -d @./scripts/v2_input.json

test-v1:
	curl -H "Content-Type: application/json" localhost:8080/v1/models/model:predict -d @./scripts/v1_input.json

test-service-v1:
	curl -k -H "Content-Type: application/json" https://fraud-chase-dev.apps.dev.rhoai.rh-aiservices-bu.com/v1/models/fraud:predict -d @./scripts/v1_input.json

test-service-v2:
	curl -k -H "Content-Type: application/json" https://fraud-chase-dev.apps.dev.rhoai.rh-aiservices-bu.com/v2/models/fraud/infer -d @./scripts/v2_input.json


