#!/bin/bash
LNS_SOLVER_DIR="${HOME}/gecode-lns"
PAR_SOLVER_DIR="${HOME}/gecode-par"
SOLVERS=(\
"${LNS_SOLVER_DIR}/build/tools/flatzinc/gecode.msc" \
"${PAR_SOLVER_DIR}/cmake-build-release/tools/flatzinc/gecode.msc" \
"${LNS_SOLVER_DIR}/build/tools/flatzinc/gecode.msc")
NUM_RUNS=( 10 10 10 )
SUFFIXES=( "lns" "par" "mab" )
FLAGS=(\
"--extra --use-pbs -p 8 --no-mab" \
"--extra -p 8 --assets 3" \
"--extra --use-pbs -p 8")
declare -a HANDLES_CSP=(\
true \
true \
true)
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
declare -a ACTIVE_PROBLEMS=( 2 3 4 6 7 8 ) #( 0 1 2 3 4   6 7 8 )
declare -a FILE_NAMES=(\
"tdtsp" \
"hrc" \
"csp-jobshop" \
"orig-tsptw" \
"csp-sb-steelmillslab" \
"sequence-tsptw" \
"rotating-workforce" \
"nurse" \
"csp-carseq")
declare -a FOLDERS=(
"${SCRIPT_DIR}/tdtsp/" \
"${SCRIPT_DIR}/hrc/" \
"${SCRIPT_DIR}/jobshop/" \
"${SCRIPT_DIR}/tsptw/" \
"${SCRIPT_DIR}/steelmill/" \
"${SCRIPT_DIR}/tsptw/" \
"${SCRIPT_DIR}/rotating-workforce/" \
"${SCRIPT_DIR}/nurse/" \
"${SCRIPT_DIR}/carseq/")
declare -a DATA_LOCATIONS=(\
"${SCRIPT_DIR}/tdtsp/dzn/*.dzn" \
"${SCRIPT_DIR}/hrc/dzn/*.dzn" \
"${SCRIPT_DIR}/jobshop/job/*-10.dzn" \
"${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn" \
"${SCRIPT_DIR}/steelmill/steel/*.dzn" \
"${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn" \
"${SCRIPT_DIR}/rotating-workforce/dzn/*.dzn" \
"${SCRIPT_DIR}/nurse/dzn/*.dzn" \
"${SCRIPT_DIR}/carseq/carseq_set_1/*.dzn")
declare -a IS_CSP=(\
false \
false \
false \
false \
false \
false \
true \
true \
true)
#  3 min timeout for COP
# 30 min timeout for CSP
# TIME_LIMITS=(180000 180000 180000 180000 180000 180000 2700000 2700000 2700000)
TIME_LIMITS=(180000 180000 180000 180000 180000 180000 180000 180000 180000)
for s in "${!SOLVERS[@]}"; do
  SOLVER=${SOLVERS[$s]}
  SUFFIX=${SUFFIXES[$s]}
  RUNS=${NUM_RUNS[$s]}
  EXTRA=${FLAGS[$s]}
  for i in "${ACTIVE_PROBLEMS[@]}"; do
    if [ "${IS_CSP[$i]}" = true ] && [ "${HANDLES_CSP[$s]}" = false ];
    then
        continue
    fi
    FILE_NAME=${FILE_NAMES[$i]}
    MZN="${FOLDERS[$i]}${FILE_NAME}.mzn"
    DATA=${DATA_LOCATIONS[$i]}
    OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt-${SUFFIX}"
    TIME_LIMIT=${TIME_LIMITS[$i]}
    if [ ${IS_CSP[$i]} = true ]; then CSP_FLAG="--csp"; else CSP_FLAG=""; fi
    echo "--solver ${SOLVER}"
    echo "         ${MZN}"
    echo "         -d ${DATA}"
    echo "         -o ${OUTPUT}"
    echo "         --time-limit ${TIME_LIMIT}"
    echo "         --num-runs ${RUNS}"
    echo "         ${CSP_FLAG}"
    echo "         ${EXTRA}"
    python3 run.py --solver ${SOLVER} \
                   ${MZN} \
                   -d ${DATA} \
                   -o ${OUTPUT} \
                   --time-limit ${TIME_LIMIT} \
                   --num-runs ${RUNS} \
                   ${CSP_FLAG} \
                   ${EXTRA}
    COMMAND_STATUS=$?
    if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi
  done
done
exit 0

FILE_NAME="csp-jobshop"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${LNS_SOLVER} \
        ${SCRIPT_DIR}/jobshop/${MZN} \
        -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_sw*.dzn \
           ${SCRIPT_DIR}/jobshop/job/jobshop_y*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${LNS_NUM_RUNS} \
        --curated-lns ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="orig-tsptw"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${LNS_SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${LNS_NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="csp-carseq"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${LNS_SOLVER} \
        ${SCRIPT_DIR}/carseq/${MZN} \
        -d ${SCRIPT_DIR}/carseq/carseq_set_1/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT_CSP} \
        --num-runs ${LNS_NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="csp-sb-steelmillslab"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${LNS_SOLVER} \
        ${SCRIPT_DIR}/steelmill/${MZN} \
        -d ${SCRIPT_DIR}/steelmill/steel/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${LNS_NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi

FILE_NAME="sequence-tsptw"
OUTPUT="${SCRIPT_DIR}/results/${FILE_NAME}.txt"
MZN="${FILE_NAME}.mzn"
python3 run.py --solver ${LNS_SOLVER} \
        ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw-orig/*.dzn \
        -o ${OUTPUT} \
        --time-limit ${TIME_LIMIT} \
        --num-runs ${LNS_NUM_RUNS} \
        ${EXTRA}
COMMAND_STATUS=$?
if [ $COMMAND_STATUS -ne 0 ]; then exit $COMMAND_STATUS; fi
