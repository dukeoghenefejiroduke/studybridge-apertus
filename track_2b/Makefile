.PHONY: build run

IMAGE_NAME ?= studybridge-apertus
PORT ?= 5000

build:
	docker build -t $(IMAGE_NAME) .

run: build
	@if [ -f ../.env ]; then \
		docker run --rm --publish $(PORT):5000 --env-file ../.env $(IMAGE_NAME); \
	else \
		docker run --rm --publish $(PORT):5000 $(IMAGE_NAME); \
	fi
