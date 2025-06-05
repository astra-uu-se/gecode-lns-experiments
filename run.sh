#!/bin/bash
SOLVER_DIR="${HOME}/dependency-curated-lns-gecode"
SOLVER="${SOLVER_DIR}/build/tools/flatzinc/gecode.msc"
EXTRA="--extra -a"
TIME_LIMIT=180000
NUM_RUNS=10
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

FILE_NAME="carseq-cc"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/carseq/${MZN} \
        -d ${SCRIPT_DIR}/carseq/carseq_set_1/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}

FILE_NAME="carseq"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/carseq/${MZN} \
        -d ${SCRIPT_DIR}/carseq/carseq_set_1/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}

FILE_NAME="jobshop-cc"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/jobshop/${MZN} \
        -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_sw*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_yl*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}

FILE_NAME="jobshop"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/jobshop/${MZN} \
        -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_sw*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_yl*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}

# FILE_NAME="dl-jobshop-cc"
# OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py --solver ${SOLVER} \
#        ${SCRIPT_DIR}/jobshop/${MZN} \
#         -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
#         -o ${OUTPUT} \
#         --time-limit ${TIME_LIMIT} \
#         --num-runs ${NUM_RUNS} \
#         --curated-lns ${EXTRA}
# 
# FILE_NAME="dl-jobshop"
# OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py --solver ${SOLVER} \
#        ${SCRIPT_DIR}/jobshop/${MZN} \
#         -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
#         -o ${OUTPUT} \
#         --time-limit ${TIME_LIMIT} \
#         --num-runs ${NUM_RUNS} \
#         ${EXTRA}
# 
# FILE_NAME="vrp-cc"
# OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py --solver ${SOLVER} \
#        ${SCRIPT_DIR}/vrp/${MZN} \
#         -d ${SCRIPT_DIR}/vrp/vrp/*.dzn \
#         -o ${OUTPUT} \
#         --time-limit ${TIME_LIMIT} \
#         --num-runs ${NUM_RUNS} \
#         --curated-lns ${EXTRA}
# 
# FILE_NAME="vrp"
# OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py --solver ${SOLVER} \
#        ${SCRIPT_DIR}/vrp/${MZN} \
#         -d ${SCRIPT_DIR}/vrp/vrp/*.dzn \
#         -o ${OUTPUT} \
#         --time-limit ${TIME_LIMIT} \
#         --num-runs ${NUM_RUNS} \
#         ${EXTRA}


FILE_NAME="sb-steelmillslab-cc"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/steelmill/${MZN} \
        -d ${SCRIPT_DIR}/steelmill/steel/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}
COMMAND_STATUS=$?
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="sb-steelmillslab"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/steelmill/${MZN} \
        -d ${SCRIPT_DIR}/steelmill/steel/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}


FILE_NAME="orig-tsptw-cc"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/orig-tsptw/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}
COMMAND_STATUS=$?
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="orig-tsptw"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/orig-tsptw/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="tsptw-cc"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}
COMMAND_STATUS=$?
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="tsptw"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="steelmillslab-cc"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${SOLVER} \
        ${SCRIPT_DIR}/steelmill/${MZN} \
        -d ${SCRIPT_DIR}/steelmill/steel/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${NUM_RUNS} \
        --curated-lns ${EXTRA}
COMMAND_STATUS=$?
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="steelmillslab"
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
#if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi