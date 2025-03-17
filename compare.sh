#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

JSON="${SCRIPT_DIR}/results_old/carseq.json ${SCRIPT_DIR}/results_old/jobshop.json ${SCRIPT_DIR}/results_old/steelmillslab.json ${SCRIPT_DIR}/results_old/tsptw.json"
python3 compare.py --json ${JSON} --plot