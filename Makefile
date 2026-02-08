.PHONY: \
	setup \
	dev \
	test \
	validate \
	gate \
	static-check \
	coverage-check \
	orchestration-start \
	orchestration-list \
	orchestration-status \
	orchestration-next \
	orchestration-validate \
	orchestration-plan \
	orchestration-iterate \
	orchestration-run \
	orchestration-archive

PYTHON ?= python3.11

setup:
	@echo "No installation step required. Use Python 3.11 and run commands via make."

dev:
	$(PYTHON) -m http.server 4173

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

validate:
	$(PYTHON) scripts/validator.py

gate:
	./scripts/gate.sh

static-check:
	$(PYTHON) scripts/static_checks.py

coverage-check:
	$(PYTHON) scripts/coverage_check.py

orchestration-start:
	@if [ -n "$(RUN_NAME)" ]; then \
		$(PYTHON) scripts/orchestration.py init "$(RUN_NAME)"; \
	else \
		$(PYTHON) scripts/orchestration.py init; \
	fi

orchestration-list:
	@$(PYTHON) scripts/orchestration.py list

orchestration-status:
	@$(PYTHON) scripts/orchestration.py status "$(RUN_ID)"

orchestration-next:
	@$(PYTHON) scripts/orchestration.py next "$(RUN_ID)"

orchestration-validate:
	@$(PYTHON) scripts/orchestration.py validate "$(RUN_ID)"

orchestration-plan:
	@$(PYTHON) scripts/orchestration.py plan "$(RUN_ID)"

orchestration-iterate:
	@$(PYTHON) scripts/orchestration.py iterate "$(RUN_ID)"

orchestration-run:
	@$(PYTHON) scripts/orchestration.py run "$(RUN_ID)"

orchestration-archive:
	@$(PYTHON) scripts/orchestration.py archive "$(RUN_ID)"
