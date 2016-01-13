#!/usr/bin/env bash

source ./env_vars.sh
export CAPABILITIES='capabilities_firefox.yaml'
cd ..

RETVALS=()
export SELENIUM_USER_AGENT='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0 codebender-selenium'
time tox tests/common/walkthrough -- --url=https://codebender.cc --source=codebender_cc
RETVALS+=($?)

export SELENIUM_USER_AGENT='Mozilla/5.0 (Windows NT 6.1; rv:43.0) Gecko/20100101 Firefox/43.0 codebender-selenium'
time tox tests/common/walkthrough -- --url=https://codebender.cc --source=codebender_cc
RETVALS+=($?)

export SELENIUM_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1; rv:43.0) Gecko/20100101 Firefox/43.0 codebender-selenium'
time tox tests/common/walkthrough -- --url=https://codebender.cc --source=codebender_cc
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
