.PHONY: test
test:
	coverage run -m unittest discover test -v
	coverage report -m


.PHONY: test-ci
test-ci:
	coverage run -m unittest discover test -v
	@coveralls


.PHONY: lint
lint:
	./scripts/lint