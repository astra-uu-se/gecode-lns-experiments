#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
MODELS=(\
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
declare -a ACTIVE_PROBLEMS=( 1 7 8 9 10 )
COMPARATIVE_MODELS=(\
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" \
"" )
NAMES=(\
"Hospitals/residents matching with couples" \
"Job shop" \
"Knapsack" \
"" \
"" \
"Steel mill slab design" \
"Time-dependent\ntravelling salesperson" \
"Travelling salesperson\nwith time windows" \
"Vehicle routing" \
"Open job shop" \
"Poetry" \
"Car sequencing" \
"Nurse rostering" \
"Rotating workforce rostering")
ACRONYMS=(\
"HRC"
"JSP" \
"KSP" \
"RCPSP" \
"RCPSPW" \
"SMSD" \
"TDTSP" \
"TSPTW" \
"VRP" \
"OJSP" \
"poet" \
"CS" \
"nurse" \
"rotating-workforce" \
)
for i in "${ACTIVE_PROBLEMS[@]}"; do
  MODEL=${MODELS[$i]}
  NAME=${NAMES[$i]}
  ACRONYM=${ACRONYMS[$i]}
  DATA="${SCRIPT_DIR}/results/${MODEL}.txt-*"
  if compgen -G "${DATA}" > /dev/null; then
    OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
    if [ -z ${COMPARATIVE_MODELS[$i]} ]; then 
    COMPARE=""
    else
    COMPARE="--comparative-data \"${COMPARATIVE_MODELS[$i]}\""
    fi
    python3 to_json.py \
            --model "${NAME}" \
            --acronym "${ACRONYM}" \
            --data ${DATA} \
            --output ${OUTPUT} \
            ${COMPARE}
  fi
done