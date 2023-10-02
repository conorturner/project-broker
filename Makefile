
run:
	uvicorn app.main:app --workers 2

dev:
	uvicorn app.main:app --reload

install:
	pip install -r requirements.txt

lint:
	pylint -j 8 app/

test:
	python -m unittest discover tests/

cover:
	coverage run -m unittest discover tests/
	coverage report -m