#!/bin/bash
EXTRA="--time-limit 7200000"
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# FILE_NAME="dl-jobshop-cc"
# OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py ${SCRIPT_DIR}/jobshop/${MZN} \
#         -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
#         -o ${OUTPUT} --curated-lns ${EXTRA}
# 
# FILE_NAME="dl-jobshop"
# OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py ${SCRIPT_DIR}/jobshop/${MZN} \
#         -d ${SCRIPT_DIR}/jobshop/job/jobshop_orb*.dzn \
#         -o ${OUTPUT} ${EXTRA}
# 
# FILE_NAME="vrp-cc"
# OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py ${SCRIPT_DIR}/vrp/${MZN} \
#         -d ${SCRIPT_DIR}/vrp/vrp/*.dzn \
#         -o ${OUTPUT} --curated-lns ${EXTRA}
# 
# FILE_NAME="vrp"
# OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
# MZN="${FILE_NAME}.mzn"
# python3 run.py ${SCRIPT_DIR}/vrp/${MZN} \
#         -d ${SCRIPT_DIR}/vrp/vrp/*.dzn \
#         -o ${OUTPUT} ${EXTRA}

FILE_NAME="orig-tsptw"
OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
MZN="${FILE_NAME}-alldiff.sat.mzn"

#SOLVER="gecode"
#python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
#        -d ${SCRIPT_DIR}/tsptw/orig-tsptw/*.dzn \
#        --solver ${SOLVER} \
#        --extra ${EXTRA}

SOLVER="chuffed"
python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/orig-tsptw/*.dzn \
        --solver ${SOLVER} \
        --extra ${EXTRA}

SOLVER="cp-sat"
python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/orig-tsptw/*.dzn \
        --solver ${SOLVER} \
        --extra ${EXTRA}


FILE_NAME="tsptw"
OUTPUT="${SCRIPT_DIR}/${FILE_NAME}.txt"
MZN="${FILE_NAME}-alldiff.sat.mzn"

#SOLVER="gecode"
#python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
#        -d ${SCRIPT_DIR}/tsptw/tsptw/*.dzn \
#        --solver ${SOLVER} \
#        --extra ${EXTRA}

SOLVER="chuffed"
python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw/*.dzn \
        --solver ${SOLVER} \
        --extra ${EXTRA}

SOLVER="cp-sat"
python3 find_initial_sol.py ${SCRIPT_DIR}/tsptw/${MZN} \
        -d ${SCRIPT_DIR}/tsptw/tsptw/*.dzn \
        --solver ${SOLVER} \
        --extra ${EXTRA}
