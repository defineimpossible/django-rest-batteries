.PHONY: example style test

example:
	python example/manage.py runserver

style:
	isort .
	brunette .

test:
	pytest
