migrate:
	poetry run python manage.py migrate

setup: migrate
	echo Create a super user
	poetry run python manage.py createsuperuser

shell:
	poetry run python manage.py shell

start: migrate
	poetry run python manage.py runserver 0.0.0.0:8000

requirements: poetry.lock
	poetry export --format requirements.txt --output requirements.txt

test:
	poetry run pytest tests

lint:
	poetry run flake8 task_manager

.PHONY: install setup shell lint test start