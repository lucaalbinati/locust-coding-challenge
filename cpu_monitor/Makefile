.PHONY: install lint format sort

install:
	pip install -r requirements.txt

lint:
	flake8 .

format:
	black .

sort:
	isort . --profile black
