.DEFAULT_GOAL := help

.PHONY: help venv clean build publishToMavenLocal

GRADLE := ./gradlew
VENV_DIR := .venv

help: ## Show all available targets
	@printf "Available targets:\n"
	@awk 'BEGIN {FS = ":.*## "} /^[[:alnum:]_-]+:.*## / {printf "  %-8s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Run ./gradlew clean
	$(GRADLE) clean

build: ## Run ./gradlew build
	$(GRADLE) build

publishToMavenLocal: ## Run ./gradlew publishToMavenLocal
	$(GRADLE) clean publishToMavenLocal


sync-oss: ##  Sync maven to oss
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install oss2
	@printf "Activate with: . $(VENV_DIR)/bin/activate\n"
	python3 scripts/sync_oss.py && python3 scripts/sync_oss.py --execute
