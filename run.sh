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
declare -a ACTIVE_PROBLEMS=( 0 1 2 3 4 5 )
declare -a FILE_NAMES=(\
"jobshop" \
"tsptw" \
"steelmillslab" \
"rotating-workforce" \
"nurse-rostering" \
"carseq")
declare -a FOLDERS=(
"${SCRIPT_DIR}/jobshop/" \
"${SCRIPT_DIR}/tsptw/" \
"${SCRIPT_DIR}/steelmillslab/" \
"${SCRIPT_DIR}/rotating-workforce/" \
"${SCRIPT_DIR}/nurse-rostering/" \
"${SCRIPT_DIR}/carseq/")
declare -a DATA_LOCATIONS=(\
"${SCRIPT_DIR}/jobshop/dzn/jobshop_swv*-10.dzn" \
"${SCRIPT_DIR}/tsptw/dzn/*.003.dzn" \
"${SCRIPT_DIR}/steelmillslab/dzn/bench_20_*.dzn" \
"${SCRIPT_DIR}/rotating-workforce/dzn/Example3*.dzn" \
"${SCRIPT_DIR}/nurse-rostering/dzn/*.dzn" \
"${SCRIPT_DIR}/carseq/dzn/car*1*dzn")
declare -a IS_CSP=(\
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
