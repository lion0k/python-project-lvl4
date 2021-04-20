migrate:
	poetry run python manage.py migrate

shell:
	poetry run python manage.py shell

start_server:
	poetry run python manage.py runserver 0.0.0.0:8000

requirements: poetry.lock
	poetry export --format requirements.txt --output requirements.txt

test:
	poetry run python manage.py test

lint:
	poetry run flake8 task_manager --exclude=migrations,task_manager/settings.py

i18n_make:
	poetry run django-admin makemessages -l ru
	poetry run django-admin makemessages -l en

i18n_compile:
	poetry run django-admin.py compilemessages -l ru
	poetry run django-admin.py compilemessages -l en

.PHONY: shell lint test