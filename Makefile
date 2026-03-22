.PHONY: install install-dev test lint format

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	python3 -m pytest tests/ -v

lint:
	pre-commit run --all-files

format:
	black multi_tenant_catalogs/ tests/
	isort multi_tenant_catalogs/ tests/
