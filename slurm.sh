#!/bin/bash
#SBATCH -A UPPMAX 2026-1-115
#SBATCH --job-name=gecode-lns-mab
#SBATCH --partition=pelle
#SBATCH --cpus-per-task=8
#SBATCH --time=5-00:00:30
MINIZINC_PATH="${HOME}/minizinc"
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
OUTPUT_DIR="${SCRIPT_DIR}/results"

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
    IS_CSP_STEMS+=${IS_CSP[$m]}
    OUTPUT_PREFIX_STEMS+=("${OUTPUT_PROBLEM_DIR}/${DZN_FILES[$d]%.*}")
  done
done

for m in ${!DZN_STEMS[@]}; do
  echo ${DZN_STEMS[$m]}
  for b in ${!MAB[@]}; do
    for ((i=1;i<=$NUM_RUNS;i++)); do
      OUTPUT_FILE="${OUTPUT_PREFIX_STEMS[$m]}-${i}.json"
      if [ ! -f ${OUTPUT_FILE} ]; then
        if [ ${IS_CSP[$i]} = true ]; then SOL_FLAG="--num-solutions 1"; else SOL_FLAG="--all-solutions"; fi
        COMMAND="${MINIZINC_PATH} ${MODEL_STEMS[$m]} \
                 solver ${SOLVER} \
                 -d ${DZN_STEMS[$m]} \
                 --json-stream \
                 --output-time \
                 --output-objective \
                 --time-limit ${TIME_LIMIT} \
                 ${SOL_FLAG} \
                 --use-pbs -p ${NUM_CORES} \
                 --output-to-file ${OUTPUT_FILE}"
        echo "$COMMAND"
      fi
    done
  done
done