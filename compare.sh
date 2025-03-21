#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

JSON="${SCRIPT_DIR}/results/carseq.json ${SCRIPT_DIR}/results/jobshop.json ${SCRIPT_DIR}/results/sb-steelmillslab.json ${SCRIPT_DIR}/results/tsptw.json"
python3 compare.py --json ${JSON}
python3 compare.py --json ${JSON} --plot