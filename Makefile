.PHONY: setup dev test validate gate

setup:
	@echo "No installation step required. Use Python 3.10+ and run commands via make."

dev:
	python3 -m http.server 4173

test:
	python3 -m unittest discover -s tests -p 'test_*.py'

validate:
	python3 scripts/validator.py data/curriculum.json

gate:
	./scripts/gate.sh
