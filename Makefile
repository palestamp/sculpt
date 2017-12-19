.PHONY: test
test:
	coverage run -m unittest discover test -v
	@coveralls

.PHONY: lint
lint:
	./scripts/lint