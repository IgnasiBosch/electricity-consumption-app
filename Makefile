
.PHONY: install
install:
	pipenv install

.PHONY: run
run:
	pipenv run python -m app


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
	isort --recursive app

.PHONY: clean
clean:
	@find . -name __pycache__ -delete -or -iname "*.py[co]" -delete
