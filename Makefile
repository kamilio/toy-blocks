.PHONY: help install format format-unsafe check test clean

help:
	@echo "Available commands:"
	@echo "  make help         - Show this help message"
	@echo "  make install      - Install project dependencies"
	@echo "  make format       - Format Python code using Ruff"
	@echo "  make format-unsafe - Format Python code using Ruff with unsafe fixes"
	@echo "  make check        - Check code for linting issues"
	@echo "  make test         - Run all tests"
	@echo "  make clean        - Remove Python cache files"

install:
	@echo "Installing dependencies..."
	python3 -m pip install -r requirements.txt
	@echo "✓ Dependencies installed"

format:
	@echo "Formatting Python files..."
	python3 -m ruff format .
	python3 -m ruff check --fix .
	@echo "✓ Code formatted"

format-unsafe:
	@echo "Formatting Python files with unsafe fixes..."
	python3 -m ruff format .
	python3 -m ruff check --fix --unsafe-fixes .
	@echo "✓ Code formatted with unsafe fixes"

check:
	@echo "Checking code for issues..."
	python3 -m ruff check .

test:
	@echo "Running tests..."
	python3 -m pytest

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"
