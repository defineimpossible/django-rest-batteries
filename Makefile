.PHONY: example style style-check test test-cov

example:
	poetry run python example/manage.py runserver

style:
	poetry run isort .
	poetry run black .

style-check:
	poetry run isort -c .
	poetry run black --check .

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=rest_batteries --cov-branch --cov-report=term:skip-covered --cov-report=html
