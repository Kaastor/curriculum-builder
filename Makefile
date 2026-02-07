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
	workflow-plan \
	workflow-iterate \
	workflow-run \
	workflow-archive

PYTHON ?= python3.11

setup:
	@echo "No installation step required. Use Python 3.11 and run commands via make."

dev:
	$(PYTHON) -m http.server 4173

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

validate:
	$(PYTHON) scripts/validator.py data/curriculum.json

gate:
	./scripts/gate.sh

workflow-start:
	@if [ -n "$(RUN_NAME)" ]; then \
		$(PYTHON) scripts/workflow.py init "$(RUN_NAME)"; \
	else \
		$(PYTHON) scripts/workflow.py init; \
	fi

workflow-list:
	@$(PYTHON) scripts/workflow.py list

workflow-status:
	@$(PYTHON) scripts/workflow.py status "$(RUN_ID)"

workflow-next:
	@$(PYTHON) scripts/workflow.py next "$(RUN_ID)"

workflow-validate:
	@$(PYTHON) scripts/workflow.py validate "$(RUN_ID)"

workflow-plan:
	@$(PYTHON) scripts/workflow.py plan "$(RUN_ID)"

workflow-iterate:
	@$(PYTHON) scripts/workflow.py iterate "$(RUN_ID)"

workflow-run:
	@$(PYTHON) scripts/workflow.py run "$(RUN_ID)"

workflow-archive:
	@$(PYTHON) scripts/workflow.py archive "$(RUN_ID)"
