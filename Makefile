DOCKERFILE		:= etc/docker/Dockerfile

IMAGE_OWNER		:= rehive
IMAGE_NAME		:= tesserarius
IMAGE_BASE		:= alpine
IMAGE_VERSION	:= $(shell cat VERSION)
IMAGE_TAG		:= $(IMAGE_OWNER)/$(IMAGE_NAME):$(IMAGE_VERSION)
CONTAINER_NAME	:= tessie

docker_build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_TAG) .

docker_push:
	docker push $(IMAGE_TAG)

docker_run:
	docker run --interactive --tty --rm $(IMAGE_TAG)

