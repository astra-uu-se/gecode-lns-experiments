#!/bin/bash
EXTRA="--time-limit 7200000"
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

FILE_NAME="sequence-tsptw"
OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
MZN="worst-${FILE_NAME}.mzn"

SOLVER="chuffed"
python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn \
        --solver ${SOLVER} \
        --extra ${EXTRA}

SOLVER="cp-sat"
python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn \
        --solver ${SOLVER} \
        --extra ${EXTRA}