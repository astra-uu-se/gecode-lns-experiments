#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

JSON="\
${SCRIPT_DIR}/results/csp-carseq.json \
${SCRIPT_DIR}/results/csp-sb-steelmillslab.json \
${SCRIPT_DIR}/results/orig-tsptw.json \
${SCRIPT_DIR}/results/rotating-workforce.json \
${SCRIPT_DIR}/results/nurse.json \
${SCRIPT_DIR}/results/csp-jobshop.json"
# ${SCRIPT_DIR}/results/hrc.json"
# ${SCRIPT_DIR}/results/tdtsp.json \
# ${SCRIPT_DIR}/results/sequence-tsptw.json \
# JSON="${SCRIPT_DIR}/results/jobshop.json \
#       ${SCRIPT_DIR}/results/precedence-jobshop.json \\
#       ${SCRIPT_DIR}/results/rcpsp.json \
#       ${SCRIPT_DIR}/results/precedence-rcpsp.json"
python3 compare-non-failing.py --json ${JSON} --skip-missing
python3 compare-non-failing.py --json ${JSON} --plot --skip-missing
