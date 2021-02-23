all: clean lint unit-test image

MAJOR_VERSION := 1
MINOR_VERSION := 0
BUILD_VERSION ?= $(USER)
VERSION := $(MAJOR_VERSION).$(MINOR_VERSION).$(BUILD_VERSION)

ORGANIZATION := clickandobey
SERVICE_NAME := datadog-json-to-terraform

PACKAGE_IMAGE_NAME := ${ORGANIZATION}-${SERVICE_NAME}-package

APP_IMAGE_NAME := ${ORGANIZATION}-${SERVICE_NAME}-app
APP_CONTAINER_NAME := ${APP_IMAGE_NAME}
GITHUB_REPO := "ghcr.io"
APP_REPO_IMAGE_NAME := ${GITHUB_REPO}/${ORGANIZATION}/${SERVICE_NAME}:${VERSION}

TEST_IMAGE_NAME := ${ORGANIZATION}-${SERVICE_NAME}-test
TEST_CONTAINER_NAME := ${TEST_IMAGE_NAME}

ROOT_DIRECTORY := `pwd`
MAIN_PATH := ${ROOT_DIRECTORY}/src/main
PYTHON_PATH := ${MAIN_PATH}/python
SCRIPTS_PATH := ${MAIN_PATH}/scripts
TEST_DIRECTORY := ${ROOT_DIRECTORY}/src/test
TEST_PYTHON_PATH := $(PYTHON_PATH):$(TEST_DIRECTORY)/python

ifneq ($(DEBUG),)
  INTERACTIVE=--interactive
  PDB=--pdb
  VERBOSE=--verbose
else
  INTERACTIVE=--env "INTERACTIVE=None"
  PDB=
  VERBOSE=
endif

ifneq (${LOUD_TESTS},)
  TEST_OUTPUT_FLAG=-s
else
  TEST_OUTPUT_FLAG=
endif

ifeq (${TEST_SPECIFIER},)
  TEST_STRING=
else
  TEST_STRING= and ${TEST_SPECIFIER}
endif

FAIL_FAST ?=
ifneq (${FAIL_FAST},)
	FAILURE_FLAG := -x
else
	FAILURE_FLAG :=
endif

package: $(shell find src/main/python -name "*") $(shell find src/main/scripts -name "*") docker/Dockerfile.package
	@docker build \
		-t ${PACKAGE_IMAGE_NAME} \
		-f docker/Dockerfile.package \
		.
	@docker run \
		--rm \
		--env VERSION=$(VERSION) \
		-v ${ROOT_DIRECTORY}/dist:/python/dist \
		${PACKAGE_IMAGE_NAME}
	@touch package

# Local App Targets

run-converter:
	@export PYTHONPATH=${PYTHON_PATH}; \
	cd ${PYTHON_PATH}; \
	pipenv run python ../scripts/convert_datadog_json_to_terraform monitor "`cat ${JSON_FILE}`" > ${OUTPUT_FILE} --verbose

# Docker App Targets

docker-build-app: package docker/Dockerfile.app
	@docker build \
		-t ${APP_IMAGE_NAME} \
		-f docker/Dockerfile.app \
		--build-arg VERSION=${VERSION} \
		.
	@touch docker-build-app

docker-run-converter: docker-build-app
	@docker run \
		--rm \
		${DETACH} \
		${INTERACTIVE} \
		--name ${APP_CONTAINER_NAME} \
		${APP_IMAGE_NAME} \
			monitor \
			"`cat ${JSON_FILE}`" > ${OUTPUT_FILE} \
			--verbose

# Tests

build-test-docker: package docker/Dockerfile.test $(shell find src/test -name "*")
	@docker build \
		-t $(TEST_IMAGE_NAME) \
		-f docker/Dockerfile.test \
		--build-arg VERSION=${VERSION} \
		.
	@touch build-test-docker

test: unit-test
test-docker: unit-test-docker

unit-test:
	@export PYTHONPATH=$(TEST_PYTHON_PATH); \
	cd $(PYTHON_PATH); \
	pipenv run pip install pytest; \
	pipenv run python -m pytest \
		--durations=10 \
		${TEST_OUTPUT_FLAG} \
		${FAILURE_FLAG} \
		-m 'unit ${TEST_STRING}' \
		../../test/python

unit-test-docker: build-test-docker
	@docker run \
		--rm \
		${INTERACTIVE} \
		--name ${TEST_CONTAINER_NAME} \
		${TEST_IMAGE_NAME} \
			--durations=10 \
			-x \
			-n 4 \
			-s \
			-m 'unit ${TEST_STRING}' \
			${PDB} \
			/test/python

# Release

release: docker-build-app github-docker-login
	@echo Tagging webservice image to ${APP_REPO_IMAGE_NAME}...
	@docker tag ${APP_IMAGE_NAME} ${APP_REPO_IMAGE_NAME}
	@echo Pushing webservice docker image to ${APP_REPO_IMAGE_NAME}...
	@docker push ${APP_REPO_IMAGE_NAME}

# Linting

lint: lint-markdown lint-python

lint-markdown:
	@echo Linting markdown files...
	@docker run \
		--rm \
		-v `pwd`:/workspace \
		wpengine/mdl \
			/workspace
	@echo Markdown linting complete.

lint-python:
	@echo Linting Python files...
	@docker build \
		-t ${SERVICE_NAME}/pylint \
		-f docker/Dockerfile.pylint \
		.
	@docker run --rm \
		${SERVICE_NAME}/pylint \
			pylint \
				--rcfile /workspace/.pylintrc \
				/src_workspace
	@echo Python linting complete

# Utilities

clean:
	@echo Cleaning Make Targets...
	@rm -f package
	@rm -f docker-build-app
	@rm -f build-test-docker
	@echo Cleaned Make Targets.
	@echo Removing Build Targets...
	@rm -rf ${ROOT_DIRECTORY}/dist
	@echo Removed Build Targets.

setup-env:
	@cd ${PYTHON_PATH}; \
	pipenv install --dev

update-dependencies:
	@cd ${PYTHON_PATH}; \
	pipenv lock

github-docker-login:
	@echo ${CR_PAT} | docker login ${GITHUB_REPO} -u ${GITHUB_USER} --password-stdin