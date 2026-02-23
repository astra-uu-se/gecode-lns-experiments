#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
MODELS=(\
"csp-carseq" \
"csp-jobshop" \
"csp-sb-steelmillslab" \
"orig-tsptw" \
"sequence-tsptw" \
"tdtsp" \
"hrc" \
"rotating-workforce" \
"nurse" \
)
COMPARATIVE_MODELS=(\
"" \
"" \
"" \
${MODELS[4]} \
${MODELS[3]} \
"" \
"" \
"" \
"" \
)
NAMES=(\
"Car sequencing" \
"Job shop" \
"Steel mill slab design" \
"Travelling salesperson\nwith time windows" \
"Travelling salesperson\nwith time windows (sequence)" \
"Time-dependent\ntravelling salesperson" \
"Hospitals/residents matching with couples" \
"Rotating workforce" \
"Nurse rostering" \
)
ACRONYMS=(\
"CS" \
"JSP" \
"SMSD" \
"TSPTW" \
"TSPTW" \
"TDTSP" \
"HRC" \
"rotating-workforce" \
"nurse" \
)
for i in "${!MODELS[@]}"; do
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