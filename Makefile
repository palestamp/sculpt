.PHONY: test
test:
	python2 -m unittest discover test

.PHONY: lint
lint:
	./scripts/lint