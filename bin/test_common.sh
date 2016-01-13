#!/usr/bin/env bash

source ./env_vars.sh
export CAPABILITIES='capabilities_firefox.yaml'
cd ..

RETVALS=()
time tox tests/common/embedded_views -- --url=https://codebender.cc --source=codebender_cc

RETVALS+=($?)
time tox tests/common/home -- --url=https://codebender.cc --source=codebender_cc
RETVALS+=($?)

time tox tests/common/sketch -- --url=https://codebender.cc --source=codebender_cc
RETVALS+=($?)

time tox tests/common/user_home -- --url=https://codebender.cc --source=codebender_cc
RETVALS+=($?)

cd -

RETVAL=0
for i in "${RETVALS[@]}"
do
    if [ ${i} -ne 0 ]; then
        RETVAL=${i}
    fi
done

echo "tests return value: ${RETVAL}"
exit ${RETVAL}
