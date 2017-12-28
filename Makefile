.PHONY: test
test:
	coverage run --source ./sculpt -m unittest discover test -v
	coverage report -m


.PHONY: test-ci
test-ci:
	coverage run --source ./sculpt -m unittest discover test -v
	@coveralls


.PHONY: lint
lint:
	./scripts/lint