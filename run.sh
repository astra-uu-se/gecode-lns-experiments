#!/bin/bash
SOLVER_DIR="${HOME}/gecode-lns"
SOLVER="${SOLVER_DIR}/build/tools/flatzinc/gecode.msc"
EXTRA="--extra --use-pbs -p 8"
TIME_LIMIT=180000
TIME_LIMIT_CSP=600000
NUM_RUNS=1
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

FILE_NAME="orig-tsptw"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="csp-carseq"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/carseq/${MZN} \
        -d ${SCRIPT_DIR}/carseq/carseq_set_1/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT_CSP} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="csp-jobshop"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/jobshop/${MZN} \
        -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_sw*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_y*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="csp-sb-steelmillslab"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/steelmill/${MZN} \
        -d ${SCRIPT_DIR}/steelmill/steel/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi