.DEFAULT_GOAL := help

.PHONY: help clean build publishToMavenLocal

GRADLE := ./gradlew

help: ## Show all available targets
	@printf "Available targets:\n"
	@awk 'BEGIN {FS = ":.*## "} /^[[:alnum:]_-]+:.*## / {printf "  %-8s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Run ./gradlew clean
	$(GRADLE) clean

build: ## Run ./gradlew build
	$(GRADLE) build

publishToMavenLocal: ## Run ./gradlew publishToMavenLocal
	$(GRADLE) clean publishToMavenLocal
