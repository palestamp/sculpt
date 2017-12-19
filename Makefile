.PHONY: test
test:
	python2 -m unittest discover test -v

.PHONY: lint
lint:
	./scripts/lint