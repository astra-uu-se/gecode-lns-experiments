#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

MODEL="carseq"
NAME="Relaxed car sequencing"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="steelmillslab"
NAME="Steel mill slab design\n(without symmetry breaking)"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="sb-steelmillslab"
NAME="Steel mill slab design\n(with symmetry breaking)"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="jobshop"
NAME="Job shop"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="dl-jobshop"
NAME="Job shop with\nearliness and tardiness costs"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="vrp"
NAME="Vehicle routing problem"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="tsptw"
NAME="Travelling salesperson\nwith time windows"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}