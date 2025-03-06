#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

MODEL="carseq"
NAME="The car sequencing problem"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="steelmillslab"
NAME="steel mill slab design problem\n(without symmetry breaking)"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="sb-steelmillslab"
NAME="steel mill slab design problem\n(with symmetry breaking)"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="jobshop"
NAME="The jobshop problem"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="dl-jobshop"
NAME="The jobshop problem with\nearliness and tardiness costs"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="vrp"
NAME="the vehicle routing problem"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}

MODEL="tsptw"
NAME="The travelling salesperson problem with time windows"
DATA="${SCRIPT_DIR}/results/${MODEL}*.txt-*"
OUTPUT="${SCRIPT_DIR}/results/${MODEL}.json"
python3 to_json.py --model "${NAME}" \
        --data ${DATA} \
        --output ${OUTPUT}