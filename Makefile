export HF_HOME=$(HOME)/goinfre/CMM/.llm
export UV_CACHE_DIR=$(HOME)/goinfre/CMM/.uv_cache
export UV_PROJECT_ENVIRONMENT=$(HOME)/goinfre/CMM/.venv

run:
	@mkdir -p data/output
	@uv run python3 src

install:
	@uv sync

debug:
	@pdb src
