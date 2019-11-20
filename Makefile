# we use the pipefail option below, which is bash specific.
SHELL := /bin/bash

.PHONY: build_docs # build the docs
build_docs:
	./docs/build.sh

.PHONY: test # run all test suites
test: test_unit test_integration

.PHONY: test_unit # run unit tests
test_unit:
	mkdir -p build
	py.test --junitxml=build/unit.xml --cov=omnibot --cov-report=xml --no-cov-on-fail tests/unit

.PHONY: coverage # build HTML coverage report
coverage:
	mkdir -p build/coverage
	py.test --cov=omnibot --cov-report=html tests/unit

.PHONY: test_integration # run integration tests
test_integration:
	mkdir -p build
	#py.test --junit-xml=build/int.xml tests/integration
