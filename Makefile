DOCKERFILE		:= etc/docker/Dockerfile

IMAGE_OWNER		:= rehive
IMAGE_NAME		:= tesserarius
IMAGE_BASE		:= alpine
IMAGE_VERSION	:= $(shell python -c "import tesserarius; print(tesserarius.__version__);")
IMAGE_TAG		:= $(IMAGE_OWNER)/$(IMAGE_NAME):$(IMAGE_VERSION)
CONTAINER_NAME	:= tessie

docker_build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_TAG) .

docker_push:
	docker push $(IMAGE_TAG)

docker_run:
	docker run --interactive --tty --rm $(IMAGE_TAG)

dist:
	python setup.py sdist bdist_wheel bdist_egg

release:
	git tag '$(IMAGE_VERSION)' -m 'Bumped to version $(IMAGE_VERSION)'
	git push origin $(IMAGE_VERSION)

build:
	python setup.py build

upload: release build dist
	python3 -m pip install --upgrade setuptools wheel twine
	python3 -m twine upload dist/* && echo 'success' > upload

clean:
	rm -rf build dist upload
