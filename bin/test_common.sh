#!/usr/bin/env bash

source ./env_vars.sh
export CAPABILITIES='capabilities_firefox.yaml'
cd ..
time tox tests/common -- --url=https://codebender.cc --source=codebender_cc
RETVAL=$?
cd -
echo "tests return value: ${RETVAL}"
exit ${RETVAL}
