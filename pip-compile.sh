#!/bin/bash
#
# This build script is based on work from https://github.com/envoyproxy/envoy/blob/master/docs/build.sh

set -e
set -x

source_venv() {
  VENV_DIR=$1
  if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [[ ! -d "${VENV_DIR}"/venv ]]; then
      virtualenv "${VENV_DIR}"/venv --python=python3.10
    fi
    source "${VENV_DIR}"/venv/bin/activate
  else
    echo "Found existing virtualenv"
  fi
}

SCRIPT_DIR=$(dirname "$0")

source_venv piptools_venv
pip install -r "${SCRIPT_DIR}"/piptools_requirements3.txt
# click 8.5 makes pip-tools 7.6.1 write a spurious --no-index into the header.
pip install pip-tools==7.6.1 click==8.4.2
pip-compile \
  --allow-unsafe \
  --annotation-style=line \
  --no-emit-index-url \
  --strip-extras \
  --output-file "${SCRIPT_DIR}"/requirements3.txt \
  "${SCRIPT_DIR}"/requirements.in \
  "${SCRIPT_DIR}"/piptools_requirements3.txt
