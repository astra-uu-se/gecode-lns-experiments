#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
MODELS=(\
"hospital-residents-with-couples" \
"jobshop" \
"knapsack" \
"rcpsp" \
"rcpsp-wet" \
"steelmillslab" \
"tdtsp" \
"tsptw" \
"vrp" \
"openshop" \
"poetry" \
"carseq" \
"nurse-rostering" \
"rotating-workforce")
declare -a ACTIVE_PROBLEMS=( 1 7 8 9 10 )
JSON=""
for i in "${ACTIVE_PROBLEMS[@]}"; do
    JSON="${JSON}${SCRIPT_DIR}/results/${MODELS[$i]}.json "
done
python3 compare-non-failing.py --json ${JSON} --skip-missing
python3 compare-non-failing.py --json ${JSON} --plot --skip-missing
