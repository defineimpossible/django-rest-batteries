.PHONY: example style style-check test

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
