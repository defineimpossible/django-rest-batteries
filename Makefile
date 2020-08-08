.PHONY: example style style-check test test-cov

example:
	python example/manage.py runserver

style:
	isort .
	brunette .

style-check:
	isort -c .
	brunette --check .

test:
	pytest

test-cov:
	pytest --cov=rest_batteries --cov-branch --cov-report=term:skip-covered --cov-report=html
