#!/bin/bash
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

PROBLEM="carseq"
JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
python3 compare.py --json ${JSON}

PROBLEM="steelmillslab"
JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
python3 compare.py --json ${JSON}

PROBLEM="sb-steelmillslab"
JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
python3 compare.py --json ${JSON}

PROBLEM="jobshop"
JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
python3 compare.py --json ${JSON}

# PROBLEM="dl-jobshop"
# # JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
# python3 compare.py --json ${JSON}

# PROBLEM="vrp"
# # JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
# python3 compare.py --json ${JSON}

PROBLEM="tsptw"
JSON="${SCRIPT_DIR}/results/${PROBLEM}.json"
python3 compare.py --json ${JSON}