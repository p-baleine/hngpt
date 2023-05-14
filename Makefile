PJ_NAME = $(shell basename $(shell pwd))

.PHONY: shell
shell:
	docker run --rm -v $(shell pwd):/app -it -p 8889:8888 \
		-e OPENAI_API_KEY=${OPENAI_API_KEY} \
		-e SERPAPI_API_KEY=${SERPAPI_API_KEY} \
		${PJ_NAME} bash

.PHONY: notebooks
notebooks:
	docker run --rm -v $(shell pwd):/app -it -p 8888:8888 \
		-e OPENAI_API_KEY=${OPENAI_API_KEY} \
		-e SERPAPI_API_KEY=${SERPAPI_API_KEY} \
		${PJ_NAME}
