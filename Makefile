.PHONY: setup run train evaluate inspect build test browser-test
setup:
	bash scripts/setup.sh
run:
	bash scripts/start.sh
train:
	.venv/bin/python -m ml.engines.train
evaluate:
	.venv/bin/python -m ml.engines.evaluate
inspect:
	.venv/bin/python -m ml.engines.inspect_data
build:
	npm --prefix frontend run build
test: build
	.venv/bin/python -m pytest -q
browser-test: build
	npm --prefix frontend run test:e2e
