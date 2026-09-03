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
declare -a PROBLEMS=(\
"hospital-residents-with-couples" \
"jobshop" \
"knapsack" \
"rcpsp" \
"rcpsp-wet" \
"steelmillslab" \
"tdptw" \
"tsptw" \
"vrp" \
"carseq" \
"nurse-rostering" \
"rotating-workforce")
declare -a IS_CSP=(\
0 \
0 \
0 \
0 \
0 \
0 \
0 \
0 \
0 \
1 \
1 \
1)
# 30 min timeout for CSP
#  3 min timeout for COP
# declare -a TIME_LIMITS=(2700000 180000)
#  3 min timeout for both:
declare -a TIME_LIMITS=(180000 180000)
for s in "${!SOLVERS[@]}"; do
  SOLVER=${SOLVERS[$s]}
  SUFFIX=${SUFFIXES[$s]}
  RUNS=${NUM_RUNS[$s]}
  EXTRA=${FLAGS[$s]}
  for i in "${ACTIVE_PROBLEMS[@]}"; do
    CSP=${IS_CSP[$i]}
    if [ "${IS_CSP[$i]}" = 1 ] && [ "${HANDLES_CSP[$s]}" = false ];
    then
        continue
    fi
    PROBLEM=${PROBLEMS[$i]}
    MZN="${SCRIPT_DIR}/${PROBLEM}/${PROBLEM}.mzn"
    DATA="${SCRIPT_DIR}/${PROBLEM}/dzn/*.dzn"
    OUTPUT="${SCRIPT_DIR}/results/${PROBLEM}.txt-${SUFFIX}"
    TIME_LIMIT=${TIME_LIMITS[$CSP]}
    if [ ${IS_CSP[$i]} = 1 ]; then CSP_FLAG="--csp"; else CSP_FLAG=""; fi
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
