.PHONY: build run

IMAGE_NAME ?= studybridge-apertus
PORT ?= 5000

build:
	docker build -t $(IMAGE_NAME) .

run: build
	docker run --rm --publish $(PORT):5000 \
		-e STUDYBRIDGE_ENABLE_LLM \
		-e LLM_BASE_URL \
		-e LLM_NAME \
		-e LLM_API_KEY \
		$(IMAGE_NAME)
