#!/bin/bash
MINIZINC_PATH="${HOME}/minizinc"
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
OUTPUT_DIR="${SCRIPT_DIR}/results"

OUTPUT_SH_PATH="${SCRIPT_DIR}/inputs.txt"

SOLVER="${HOME}/gecode-lns/build/tools/flatzinc/gecode.msc" \

NUM_CORES=8
TIME_LIMIT=180000

declare -a PROBLEMS=(\
"jobshop" \
"tsptw" \
"steelmillslab" \
"rotating-workforce" \
"nurse-rostering" \
"carseq")

declare -a IS_CSP=(\
false \
false \
false \
true \
true \
true)

declare -a MAB=(\
"GreedyBandit" \
"RoundRobinBandit" \
"UCBBandit" \
"SoftMaxBandit" \
"Exp3Bandit" \
"ThompsonBandit" \
"DiscountedUCBBandit" \
"SlidingWindowUCBBandit" \
"DiscountedThompsonBandit" \
"SlidingWindowThompsonBandit" \
"FDiscountedSlidingWindowThompsonBandit" \
"RavenBandit")

declare -a MAB_IS_USED=(\
true \
false \
false \
false \
false \
false \
false \
false \
false \
false \
false \
false)

NUM_RUNS=5

# Read the dzn names into an array
declare -a MODEL_STEMS=()
declare -a DZN_STEMS=()
declare -a IS_CSP_STEMS=()
declare -a OUTPUT_PREFIX_STEMS=()
for m in "${!PROBLEMS[@]}"; do
  DZN_STEMS_FILE="${SCRIPT_DIR}/${PROBLEMS[$m]}/inputs.txt"
  OUTPUT_PROBLEM_DIR="${OUTPUT_DIR}/${PROBLEMS[$m]}"
  mkdir -p ${OUTPUT_PROBLEM_DIR}
  readarray -t DZN_FILES < ${DZN_STEMS_FILE}
  for d in ${!DZN_FILES[@]}; do
    MODEL_STEMS+=("${SCRIPT_DIR}/${PROBLEMS[$m]}/${PROBLEMS[$m]}.mzn")
    DZN_STEMS+=("${SCRIPT_DIR}/${PROBLEMS[$m]}/dzn/${DZN_FILES[$d]}")
    IS_CSP_STEMS+=(${IS_CSP[$m]})
    OUTPUT_PREFIX_STEMS+=("${OUTPUT_PROBLEM_DIR}/${DZN_FILES[$d]%.*}")
  done
done

declare -a JOBS=()
for m in ${!DZN_STEMS[@]}; do
  echo ${MODEL_STEMS[$m]}
  if [ ${IS_CSP_STEMS[$m]} = false ]; then SOL_FLAG="--num-solutions 1"; else SOL_FLAG="--all-solutions"; fi
  for b in ${!MAB[@]}; do
    if [ ${MAB_IS_USED[$b]} = false ]; then
      continue
    fi
    for ((i=0;i<=$NUM_RUNS;i++)); do
      OUTPUT_FILE="${OUTPUT_PREFIX_STEMS[$m]}-mab-${b}-${i}.json"
      if [ -f ${OUTPUT_FILE} ]; then
        continue
      fi
      JOBS+=("${MINIZINC_PATH} ${MODEL_STEMS[$m]} --solver ${SOLVER} -d ${DZN_STEMS[$m]} --json-stream --output-time --output-objective --time-limit ${TIME_LIMIT} ${SOL_FLAG} --output-to-file ${OUTPUT_FILE} --use-pbs -p ${NUM_CORES} --mab-type ${b}")
    done
  done
done

echo "$COMMAND" >> ${OUTPUT_SH_PATH}
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