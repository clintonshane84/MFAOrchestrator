.PHONY: run test lint type fmt

run:
\tuvicorn app.main:app --reload

test:
\tpytest

lint:
\truff check .

type:
\tmypy app

fmt:
\truff check . --fix
