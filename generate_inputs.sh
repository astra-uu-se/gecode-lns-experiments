#!/bin/bash
MINIZINC_PATH="${HOME}/minizinc"
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
OUTPUT_DIR="${SCRIPT_DIR}/results-slurm"

OUTPUT_SH_PATH="${SCRIPT_DIR}/inputs.txt"

SOLVER="${HOME}/gecode-ls/build/tools/flatzinc/gecode.msc" \

NUM_CORES=8
TIME_LIMIT=180000

declare -a ACTIVE_PROBLEMS=( 1 7 8 9 10 )
declare -a PROBLEMS=(\
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

declare -a SOLVER_EXT=(\
"gen" \
"nei" )

SOLVER_FLAGS=(\
"--portfolio --no-systematic --generic" \
"--portfolio --no-systematic" )

NUM_RUNS=5

mkdir -p ${OUTPUT_DIR}
# Read the dzn names into an array
declare -a MODEL_STEMS=()
declare -a DZN_STEMS=()
declare -a OUTPUT_PREFIX_STEMS=()
for m in "${ACTIVE_PROBLEMS[@]}"; do
  DZN_STEMS_FILE="${SCRIPT_DIR}/${PROBLEMS[$m]}/inputs.txt"
  OUTPUT_PROBLEM_DIR="${OUTPUT_DIR}/${PROBLEMS[$m]}"
  mkdir -p ${OUTPUT_PROBLEM_DIR}
  readarray -t DZN_FILES < ${DZN_STEMS_FILE}
  for d in ${!DZN_FILES[@]}; do
    MODEL_STEMS+=("${SCRIPT_DIR}/${PROBLEMS[$m]}/${PROBLEMS[$m]}.mzn")
    DZN_STEMS+=("${SCRIPT_DIR}/${PROBLEMS[$m]}/dzn/${DZN_FILES[$d]}")
    OUTPUT_PREFIX_STEMS+=("${OUTPUT_PROBLEM_DIR}/${DZN_FILES[$d]%.*}")
  done
done

declare -a JOBS=()
for s in ${!SOLVER_EXT[@]}; do
  for m in ${!MODEL_STEMS[@]}; do
    echo ${MODEL_STEMS[$m]}
    SOL_FLAG="--all-solutions"
    for ((i=0;i<=$NUM_RUNS;i++)); do
      OUTPUT_FILE="${OUTPUT_PREFIX_STEMS[$m]}-${SOLVER_EXT[$s]}-${i}.json"
      if [ -f ${OUTPUT_FILE} ]; then
        continue
      fi
      JOBS+=(\
"${MINIZINC_PATH} \
${MODEL_STEMS[$m]} \
--solver ${SOLVER} -d \
${DZN_STEMS[$m]} \
--time-limit ${TIME_LIMIT} \
${SOL_FLAG} \
--output-to-file ${OUTPUT_FILE} \
-p ${NUM_CORES} \
${SOLVER_FLAGS[$s]} \
--json-stream \
--output-time \
--output-objective" )
    done
  done
done

NUM_COMMANDS_PER_JOB=10
UB=$((${NUM_COMMANDS_PER_JOB} - 1))
i=0
BUFFER=""
FIRST=true
for j in ${!JOBS[@]}; do
  BUFFER="${BUFFER}${JOBS[$j]}"
  if [ "$i" -lt "${UB}" ]; then 
    BUFFER="${BUFFER};"
    i=$(($i + 1))
  else
    if [ "${FIRST}" = true ]; then
      echo "${BUFFER}" > ${OUTPUT_SH_PATH}
      FIRST=false
    else 
      echo "${BUFFER}" >> ${OUTPUT_SH_PATH}
    fi
    BUFFER=""
    i=0
  fi
done

if [ ! -z "${BUFFER}" ]; then
  echo "${BUFFER}" >> ${OUTPUT_SH_PATH}
  BUFFER=""
fi