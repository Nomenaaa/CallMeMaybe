export HF_HOME=$(HOME)/goinfre/CMM/.llm
export UV_CACHE_DIR=$(HOME)/goinfre/CMM/.uv_cache
export UV_PROJECT_ENVIRONMENT=$(HOME)/goinfre/CMM/.venv

run:
	@mkdir -p data/output
	@uv run python3 src

install:
	@uv sync

debug:
	@uv run python3 -m pdb src/__main__.py

clean:
	@find . -type d -name "*cache*" | xargs rm -rf

lint:
	@uv run flake8 src --exclude=.venv,__pycache__,.mypy_cache
	@uv run mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs
	@$(MAKE) -s clean
