.PHONY: help bootstrap project-validate validate verify test security

help:
	@echo "jee-agentic-dev commands:"
	@echo "  make bootstrap         - Show project inception/bootstrap guidance"
	@echo "  make project-validate  - Validate .ai/project.json"
	@echo "  make validate          - Validate all task/report state"
	@echo "  make verify            - Run full repository verification"
	@echo "  make test              - Run testing verification only"
	@echo "  make security          - Run security verification only"

bootstrap:
	python scripts/agentctl.py bootstrap

project-validate:
	python scripts/agentctl.py project validate

validate:
	python scripts/agentctl.py task validate

verify:
	python scripts/agentctl.py verify

test:
	python scripts/agentctl.py verify --tests-only

security:
	python scripts/agentctl.py verify --security-only
