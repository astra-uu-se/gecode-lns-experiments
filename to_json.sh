#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
MODELS=(\
"carseq" \
"steelmillslab" \
"sb-steelmillslab" \
"jobshop" \
"precedence-jobshop" \
"rcpsp" \
"precedence-rcpsp" \
"dl-jobshop" \
"vrp" \
"tsptw" \
"orig-tsptw" \
)
COMPARATIVE_MODELS=(\
"" \
"" \
${MODELS[4]} \
${MODELS[3]} \
${MODELS[5]} \
${MODELS[4]} \
"" \
"" \
"" \
"" \
"" \
)
NAMES=(\
"Relaxed car sequencing" \
"Steel mill slab design\n(without symmetry breaking)" \
"Steel mill slab design" \
"Job shop" \
"Job shop with precedences" \
"RCPSP" \
"RCPSP with precedences" \
"Job shop with\nearliness and tardiness costs" \
"Vehicle routing problem" \
"Travelling salesperson\nwith time windows" \
"Travelling salesperson\nwith time windows" \
)
ACRONYMS=(\
"RCS" \
"SMSD (w/o symmetry breaking)" \
"SMSD" \
"JSP" \
"JSP-P" \
"RCPSP" \
"RCPSP-P" \
"JSP-ETC" \
"VRP" \
"TSPTW" \
"TSPTW" \
)
for i in "${!MODELS[@]}"; do
  MODEL=${MODELS[$i]}
  NAME=${NAMES[$i]}
  ACRONYM=${ACRONYMS[$i]}
  DATA="${SCRIPT_DIR}/results/${MODEL}*.txt"
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
exit 0

MODEL="carseq"
NAME="Relaxed car sequencing"
ACRONYM="RCS"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="steelmillslab"
NAME="Steel mill slab design\n(without symmetry breaking)"
ACRONYM="SMSD (w/o symmetry breaking)"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="sb-steelmillslab"
NAME="Steel mill slab design"
ACRONYM="SMSD"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="jobshop"
NAME="Job shop"
P_MODEL="precedence-${MODEL}"
ACRONYM="JSP"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
P_DATA="${SCRIPT_DIR}/results/${P_MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --comparative-data ${P_DATA} \
        --output ${OUTPUT}

NAME="Job shop with precedences"
ACRONYM="JSP-P"
OUTPUT="${SCRIPT_DIR}/results/${P_MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${P_DATA} \
        --comparative-data ${DATA} \
        --output ${OUTPUT}

MODEL="rcpsp"
P_MODEL="precedence-${MODEL}"
NAME="RCPSP"
ACRONYM="RCPSP"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
P_DATA="${SCRIPT_DIR}/results/${P_MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

NAME="RCPSP with precedences"
ACRONYM="RCPSP-P"
OUTPUT="${SCRIPT_DIR}/results/${P_MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${P_DATA} \
        --comparative-data ${DATA} \
        --output ${OUTPUT}

MODEL="dl-jobshop"
NAME="Job shop with\nearliness and tardiness costs"
ACRONYM="JSP-ETC"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="vrp"
NAME="Vehicle routing problem"
ACRONYM="VRP"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="tsptw"
NAME="Travelling salesperson\nwith time windows"
ACRONYM="TSPTW"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="orig-tsptw"
NAME="Travelling salesperson\nwith time windows"
ACRONYM="TSPTW"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
        --output ${OUTPUT}