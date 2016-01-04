#!/usr/bin/env bash

source ./env_vars.sh
export CAPABILITIES='capabilities_firefox.yaml'
cd ..
time tox tests/libraries -- --url=https://codebender.cc --source=codebender_cc -F
RETVAL=$?
cd -
echo "tests return value: ${RETVAL}"
exit ${RETVAL}
