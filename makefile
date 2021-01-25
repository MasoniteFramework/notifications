.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Install package dependencies
	cp .env-example .env
	pip install --upgrade pip
	# install test project and package dependencies
	pip install -r requirements.txt
	# install package
	pip install .
	# install dev dependencies (services are need for tests and dev for publishing)
	pip install .[test,dev,services]
test: ## Run package tests
	python -m pytest tests
ci: ## [CI] Run package tests and lint
	make test
	make lint
lint: ## Run code linting
	python -m flake8 src/masonite/notifications/ --ignore=E501,F401,E128,E402,E731,F821,E712,W503
format: ## Format code with Black
	black src/masonite/notifications
deepsource:
	curl https://deepsource.io/cli | sh
	./bin/deepsource report --analyzer test-coverage --key python --value-file ./coverage.xml
coverage: ## Run package tests and upload coverage reports
	python -m pytest --cov-report term --cov-report xml --cov=src/masonite tests/
	python -m coveralls --service=github
publish: ## Publish package to pypi
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg masonite.egg-info
