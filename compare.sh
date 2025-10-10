#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

JSON="${SCRIPT_DIR}/results/carseq.json ${SCRIPT_DIR}/results/jobshop.json ${SCRIPT_DIR}/results/steelmillslab.json ${SCRIPT_DIR}/results/orig-tsptw.json"
# JSON="${SCRIPT_DIR}/results/jobshop.json \
#       ${SCRIPT_DIR}/results/precedence-jobshop.json \\
#       ${SCRIPT_DIR}/results/rcpsp.json \
#       ${SCRIPT_DIR}/results/precedence-rcpsp.json"
python3 compare.py --json ${JSON} --skip-missing
python3 compare.py --json ${JSON} --plot --skip-missing
