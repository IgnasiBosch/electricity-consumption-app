
main_image := econsumption:latest

.PHONY: install
install:
	pipenv install

.PHONY: run-locally
run-locally:
	pipenv run python -m app


.PHONY: build
build:
	docker build --tag $(main_image) .

.PHONY: run
run:
	docker-compose --project-name econsumption up app

.PHONY: ci
ci:
	touch ./coverage.xml
	make clean-images
	docker-compose --project-name $(service)-ci run --rm ci
	@sed -i 's,<source>\/app<\/source>,<source>'./'<\/source>,g' coverage.xml

# CLEANING
# =======================================================
.PHONY: clean-images
clean-images:
	docker rmi --force $(main_image)

.PHONY: clean
clean:
	@find . -name __pycache__ -delete -or -iname "*.py[co]" -delete


# DEVELOPMENT
# =======================================================
.PHONY: install-dev
install-dev:
	pipenv install -d

.PHONY: style
style:
	pipenv run black .

.PHONY: isort
isort:
	pipenv run isort --recursive app

.PHONY: lint
lint:
	pipenv run pylint app --rcfile=setup.cfg

# LOCAL TESTING
# =======================================================
.PHONY: test
test:
	pipenv run coverage run --source app -m pytest tests --color=yes
	pipenv run coverage report

.PHONY: unit-test
unit-test:
	pipenv run pytest tests/unit