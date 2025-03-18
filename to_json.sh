#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

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
ACRONYM="JSP"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" --acronym "${ACRONYM}" \
        --data ${DATA} \
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