MKFILE_PATH=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
GENERATE_INPUTS=${MKFILE_PATH}generate_inputs.sh
INPUTS_PATH=${MKFILE_PATH}inputs.txt
SLURM_SCRIPT=${MKFILE_PATH}slurm.sh
SLURM_ARRAY_TASK_MIN=1

.PHONY: all
all: run

.PHONY: generate_inputs
generate_inputs:
	bash ${GENERATE_INPUTS}

.PHONY: run
run: generate_inputs
	$(eval SLURM_ARRAY_TASK_MAX := $(shell wc -l < ${INPUTS_PATH}))
	sbash --array=${SLURM_ARRAY_TASK_MIN}-${SLURM_ARRAY_TASK_MAX} \
	      -N1 ${SLURM_SCRIPT}

.PHONY: default
default: run
