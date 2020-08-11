test:
	python -m pytest --cov=pssexec --cov-report term-missing

lint:
	pylint pssexec/ tests/

checklist: lint test

.PHONY: test lint checklist
