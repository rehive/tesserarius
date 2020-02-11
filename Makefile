DOCKERFILE					:= etc/docker/Dockerfile
TEMPLATE_DOCKERFILE			:= etc/docker/dev-template.Dockerfile
TEMPLATE_IMAGE_NAME			:= dev-template
IMAGE_OWNER					:= rehive
IMAGE_NAME					:= tesserarius
IMAGE_BASE					:= alpine
HASH_TAG					:= $(shell git rev-parse --short HEAD)
IMAGE_VERSION				:= $(shell python -c "import tesserarius; print(tesserarius.__version__);")
IMAGE_PRE_TAG				:= $(IMAGE_OWNER)/$(IMAGE_NAME)
TEMPLATE_IMAGE_PRE_TAG		:= $(IMAGE_OWNER)/$(TEMPLATE_IMAGE_NAME)
CONTAINER_NAME				:= tessie
AUTH_CONTAINER_NAME 		:= google_auth

auth:
	docker run --name $(AUTH_CONTAINER_NAME) -it google/cloud-sdk:255.0.0-alpine \
		/bin/bash -c "gcloud auth application-default login; gcloud auth login"
	mkdir -p var/.config
	docker cp $(AUTH_CONTAINER_NAME):/root/.config/gcloud var/.config/gcloud
	docker container rm $(AUTH_CONTAINER_NAME)

docker_build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_PRE_TAG):latest .
	docker build -f $(DOCKERFILE) -t $(IMAGE_PRE_TAG):$(IMAGE_VERSION) .
	docker build -f $(DOCKERFILE) -t $(IMAGE_PRE_TAG):$(HASH_TAG) .

template_docker_build:
	docker build -f $(TEMPLATE_DOCKERFILE) -t $(TEMPLATE_IMAGE_PRE_TAG):latest .
	docker build -f $(TEMPLATE_DOCKERFILE) -t $(TEMPLATE_IMAGE_PRE_TAG):$(IMAGE_VERSION) .
	docker build -f $(TEMPLATE_DOCKERFILE) -t $(TEMPLATE_IMAGE_PRE_TAG):$(HASH_TAG) .

docker_push:
	docker push $(IMAGE_PRE_TAG):latest
	docker push $(IMAGE_PRE_TAG):$(IMAGE_VERSION)
	docker push $(IMAGE_PRE_TAG):$(HASH_TAG)
	docker push $(TEMPLATE_IMAGE_PRE_TAG):latest
	docker push $(TEMPLATE_IMAGE_PRE_TAG):$(IMAGE_VERSION)
	docker push $(TEMPLATE_IMAGE_PRE_TAG):$(HASH_TAG)

docker_run:
	docker run -it --rm \
		-v $$PWD/etc/tesserarius/roles.yaml:/rehive/tesserarius/etc/tesserarius/roles.yaml \
		$(IMAGE_PRE_TAG):latest

dist:
	python setup.py sdist bdist_wheel bdist_egg

release:
	git tag '$(IMAGE_VERSION)' -m 'Bumped to version $(IMAGE_VERSION)'
	git push origin $(IMAGE_VERSION)

build:
	python setup.py build

upload:
	python3 -m pip install --upgrade pip setuptools wheel twine
	python3 -m twine upload dist/* && echo 'success' > upload

all: release build dist upload

clean:
	rm -rf build dist upload
	docker container rm $(AUTH_CONTAINER_NAME)
	docker container rm $(CONTAINER_NAME)
