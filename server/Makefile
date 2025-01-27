.PHONY: install lint format sort build up down

IMAGE_NAME=locust-coding-challenge
IMAGE_VERSION=1.0.0

DOCKER_IMAGE = lucaalbinati/$(IMAGE_NAME):$(IMAGE_VERSION)

install:
	pip install -r requirements.txt

lint:
	flake8 .

format:
	black .

sort:
	isort . --profile black

build:
	docker build --platform linux/amd64 -t $(DOCKER_IMAGE) .

up:
	DOCKER_DEFAULT_PLATFORM=linux/amd64 docker-compose up

down:
	docker-compose down
