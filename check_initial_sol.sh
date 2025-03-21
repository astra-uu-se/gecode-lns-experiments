#!/bin/bash
EXTRA="--time-limit 7200000"
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

FILE_NAME="tsptw"
OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
MZN="${FILE_NAME}-checker.mzn"

python3 check_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw/*.dzn
