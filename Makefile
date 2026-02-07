.PHONY: \
	setup \
	dev \
	test \
	validate \
	gate \
	workflow-start \
	workflow-list \
	workflow-status \
	workflow-next \
	workflow-validate \
	workflow-run \
	workflow-archive

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

workflow-start:
	@if [ -n "$(RUN_NAME)" ]; then \
		python3 scripts/workflow.py init "$(RUN_NAME)"; \
	else \
		python3 scripts/workflow.py init; \
	fi

workflow-list:
	@python3 scripts/workflow.py list

workflow-status:
	@python3 scripts/workflow.py status "$(RUN_ID)"

workflow-next:
	@python3 scripts/workflow.py next "$(RUN_ID)"

workflow-validate:
	@python3 scripts/workflow.py validate "$(RUN_ID)"

workflow-run:
	@python3 scripts/workflow.py run "$(RUN_ID)"

workflow-archive:
	@python3 scripts/workflow.py archive "$(RUN_ID)"
