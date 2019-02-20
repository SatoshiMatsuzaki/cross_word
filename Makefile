MODEL_NAME := crossword

clean: clean-pyc

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

## build
build:
	docker build -t $(MODEL_NAME)/dev:latest .

## bash
bash:
	docker run \
		-p 8080:8000 \
		-v $(CURDIR)/crossword/:/work/crossword \
		-it $(MODEL_NAME)/dev:latest \
		/bin/bash


## lint using flake8
flake8:
	docker run -it $(MODEL_NAME)/dev:latest flake8 .

## run
run-jupyter:
	docker run \
		-p 8899:8889 \
		-v $(CURDIR)/notebooks/:/app/notebooks \
		$(MODEL_NAME)/dev:latest \
		jupyter notebook --no-browser --ip=0.0.0.0 --port 8889 --allow-root
