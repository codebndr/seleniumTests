#!/usr/bin/env bash

source ./env_vars.sh
export CAPABILITIES='capabilities_firefox.yaml'
export CODEBENDER_SELENIUM_HUB_URL="http://127.0.0.1:4444/wd/hub"
cd ..
time tox tests/libraries -- --url=https://codebender.cc --source=codebender_cc -F
RETVAL=$?
cd -
echo "tests return value: ${RETVAL}"
exit ${RETVAL}
