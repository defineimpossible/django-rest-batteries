.PHONY: example check lint test test-cov

example:
	poetry run python example/manage.py runserver

check:
	poetry run black --check .
	poetry run ruff check .

lint:
	poetry run black .
	poetry run ruff --fix .

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=rest_batteries --cov-branch --cov-report=term:skip-covered --cov-report=html
	poetry run coverage xml
