run:
	@uv run python3 -m src

install:
	@uv sync

debug:
	@uv run python3 -m pdb src/__main__.py

clean:
	@find . -type d -name "*cache*" | xargs rm -rf

lint:
	@uv run python3 -m flake8 src/ --docstring-convention=google --exclude=.venv,__pycache__,.mypy_cache
	@uv run python3 -m mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs
	@$(MAKE) -s clean
