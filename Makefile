migrate:
	poetry run python manage.py migrate

setup:
	echo Create a super user
	poetry run python manage.py createsuperuser

shell:
	poetry run python manage.py shell

start:
	poetry run python manage.py runserver 0.0.0.0:8000

requirements: poetry.lock
	poetry export --format requirements.txt --output requirements.txt

test:
	poetry run pytest tests

lint:
	poetry run flake8 task_manager

i18n_make:
	poetry run django-admin makemessages -l ru
	poetry run django-admin makemessages -l en

i18n_compile:
	poetry run django-admin.py compilemessages -l ru
	poetry run django-admin.py compilemessages -l en

.PHONY: install setup shell lint test start