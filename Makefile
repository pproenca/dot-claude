# Claude Code Plugins Marketplace Makefile
# Run 'make help' for available targets

.DELETE_ON_ERROR:
.DEFAULT_GOAL := all

# ============================================================================
# Configuration
# ============================================================================

# Override via environment or command line: make test BATS=path/to/bats
BATS ?= bats
SHELLCHECK ?= shellcheck
PRE_COMMIT ?= uv run pre-commit

# Plugin directories
PLUGIN_DIR := plugins
DEV_WORKFLOW := $(PLUGIN_DIR)/dev-workflow
DEV_PYTHON := $(PLUGIN_DIR)/dev-python

# ============================================================================
# Computed Variables
# ============================================================================

# All bash scripts to lint
BASH_SCRIPTS := $(wildcard $(DEV_WORKFLOW)/scripts/*.sh) \
                $(wildcard $(DEV_WORKFLOW)/hooks/*.sh) \
                $(wildcard $(DEV_WORKFLOW)/skills/*/find-polluter.sh) \
                $(wildcard $(DEV_PYTHON)/hooks/*.sh)

# All test files
TEST_FILES := $(wildcard $(DEV_WORKFLOW)/tests/*.bats)

# ============================================================================
# Targets
# ============================================================================

##@ Setup

.PHONY: all
all: install  ## Default: bootstrap project for development

.PHONY: install
install:  ## Install all dependencies (bats, shellcheck, pre-commit via uv)
	@echo "Installing development dependencies..."
	@if ! command -v $(BATS) &>/dev/null; then \
		echo "Installing bats-core..."; \
		if [ "$$(uname)" = "Darwin" ]; then \
			brew install bats-core; \
		else \
			sudo apt-get update && sudo apt-get install -y bats; \
		fi; \
	else \
		echo "✓ bats-core already installed"; \
	fi
	@if ! command -v $(SHELLCHECK) &>/dev/null; then \
		echo "Installing shellcheck..."; \
		if [ "$$(uname)" = "Darwin" ]; then \
			brew install shellcheck; \
		else \
			sudo apt-get update && sudo apt-get install -y shellcheck; \
		fi; \
	else \
		echo "✓ shellcheck already installed"; \
	fi
	@echo "Installing Python dependencies via uv..."
	uv sync
	@if [ -f .pre-commit-config.yaml ]; then \
		echo "Installing pre-commit hooks..."; \
		$(PRE_COMMIT) install; \
	fi
	@echo "✓ Setup complete"

.PHONY: deps
deps:  ## Check dependencies status
	@$(DEV_WORKFLOW)/scripts/check-dependencies.sh

##@ Testing

.PHONY: test
test:  ## Run all bats tests
	$(BATS) $(DEV_WORKFLOW)/tests/

.PHONY: test-verbose
test-verbose:  ## Run tests with verbose output
	$(BATS) --verbose-run $(DEV_WORKFLOW)/tests/

##@ Code Quality

.PHONY: lint
lint:  ## Check code with shellcheck (no auto-fix)
	@echo "Running shellcheck on bash scripts..."
	@failed=0; \
	for f in $(BASH_SCRIPTS); do \
		if [ -f "$$f" ]; then \
			if $(SHELLCHECK) -x "$$f" >/dev/null 2>&1; then \
				echo "[OK] $$(basename $$f)"; \
			else \
				echo "[ERR] $$(basename $$f)"; \
				$(SHELLCHECK) -x "$$f" || true; \
				failed=1; \
			fi; \
		fi; \
	done; \
	exit $$failed

.PHONY: validate
validate:  ## Run plugin-specific validation (JSON, frontmatter, permissions)
	@echo "=== Claude Plugin Validation ==="
	@for dir in $(PLUGIN_DIR)/*/; do \
		echo "Validating $$(basename $$dir)..."; \
		claude plugin validate "$$dir" || exit 1; \
	done
	@echo ""
	@echo "=== Validating dev-workflow ==="
	@$(DEV_WORKFLOW)/scripts/validate.sh
	@echo ""
	@echo "=== All plugins validated ==="

.PHONY: check
check:  ## Run all validation (marketplace levels 1-6 + BATS tests)
	@scripts/validate-all.sh

##@ Cleanup

.PHONY: clean
clean:  ## Remove generated files and caches
	$(RM) -r .claude/dev-workflow-state.local.md
	$(RM) -r **/__pycache__
	$(RM) -r **/.pytest_cache
	@echo "✓ Cleaned"

##@ Help

.PHONY: help
help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)
