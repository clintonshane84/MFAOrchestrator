.PHONY: run test lint type fmt

run:
\tuvicorn app.main:app --reload --host 0.0.0.0 --port 8000


test:
\tpytest

lint:
\truff check .

type:
\tmypy app

fmt:
\truff check . --fix
