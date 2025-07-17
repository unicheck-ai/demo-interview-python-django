.PHONY: help env install ruff-format ruff-lint django-check init setup lint test run shell interview migrate makemigrations database-reset
-include .env
export

POSTGRES_DB ?= appdb
POSTGRES_USER ?= dbuser
POSTGRES_PASSWORD ?= dbpassword

# Default target executed when no arguments are given to make.
help:
	@echo "Makefile Commands:"
	@echo "  env         	: Local setup"
	@echo "  install        : Installs Python dependencies from requirements.txt."
	@echo "  ruff-format    : Formats code using Ruff."
	@echo "  ruff-lint      : Lints code using Ruff."
	@echo "  django-check   : Run Django checks."
	@echo "  interview 		: Runs tests for the interview."
	@echo "  migrate        : Applies database migrations."
	@echo "  makemigrations : Creates new database migrations for the 'app' app."
	@echo "  database-reset : Resets the database by dropping and recreating it, and clearing migrations."
	@echo "  init           : Initializes the environment and installs dependencies."
	@echo "  setup          : Initializes the environment, installs dependencies, and applies migrations."
	@echo "  lint           : Runs code formatting and linting checks."
	@echo "  test           : Runs the test suite using pytest."
	@echo "  run            : Starts the Django development server."
	@echo "  shell          : Opens the Django shell."


env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
	fi
	
install:
	pip3 install -r requirements.txt --root-user-action=ignore

# Development tasks
ruff-format:
	python3 -m ruff format .

ruff-lint:
	python3 -m ruff check . --fix

django-check:
	python3 manage.py check

# Django commands
migrate:
	python3 manage.py migrate

makemigrations:
	python3 manage.py makemigrations app

dbreset:
	PGPASSWORD=$(POSTGRES_PASSWORD) dropdb --if-exists -h db -U $(POSTGRES_USER) $(POSTGRES_DB)
	PGPASSWORD=$(POSTGRES_PASSWORD) createdb -h db -U $(POSTGRES_USER) $(POSTGRES_DB)
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc" -delete
	python manage.py flush --no-input

run:
	python3 manage.py runserver 0.0.0.0:8000

shell:
	python3 manage.py shell

# General

init: env install 

setup: init makemigrations migrate

lint: ruff-format ruff-lint django-check

test:
	python3 -m pytest

interview:
	@if [ -n "$$target" ]; then \
		python3 -m pytest $$target; \
	else \
		python3 -m pytest tests/interview/; \
	fi
