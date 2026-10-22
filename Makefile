.DEFAULT_GOAL := help
SHELL := /bin/bash

PORT ?= 1313
BIND ?= 127.0.0.1

.PHONY: help serve draft build clean rebuild check deploy-check

help: ## Show this help
	@echo "hugo-web - available targets:"
	@echo
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Variables: PORT=$(PORT) BIND=$(BIND)  (override: make serve PORT=1413)"

serve: ## Production-like preview (drafts excluded)
	hugo server --bind $(BIND) --port $(PORT)

draft: ## Dev preview with drafts and future-dated pages
	hugo server -D --buildFuture --navigateToChanged --bind $(BIND) --port $(PORT)

build: ## Build static site into public/
	hugo --gc --minify

rebuild: clean build ## Clean then build from scratch

check: ## Build with verbose output to surface warnings
	hugo --gc --logLevel info

clean: ## Remove generated output and caches
	rm -rf public resources .hugo_build.lock
	@echo "cleaned: public/ resources/ .hugo_build.lock"

deploy-check: build ## Build and report what would be published
	@echo
	@echo "Built $(shell find public -name '*.html' | wc -l) HTML pages," \
	     "total $$(du -sh public | cut -f1)"
	@echo "Upload the contents of public/ to your web root."
