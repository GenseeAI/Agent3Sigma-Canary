#!/bin/bash
# Batch run: memory attack test (models × images, parallel, no attack methods)
#
# Usage:
#   ./batch_run/memory.sh              # Full memory suite
#   ./batch_run/memory.sh example      # 10 representative samples
#   MAX_PARALLEL=4 ./batch_run/memory.sh example

set +e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_lib.sh"
load_batch_config "$SCRIPT_DIR"
init_parallel

## Suite selection
SAMPLE_SUITE="task_20001,task_20009,task_20019,task_20031,task_20041,task_25001,task_25006,task_25010,task_25014,task_25019"

if [ "$1" = "example" ] || [ "$1" = "sample" ]; then
    SUITE_ARGS="--suite $SAMPLE_SUITE"
    RUN_TAG="example"
    echo ">>> Mode: sample (10 tasks)"
else
    SUITE_ARGS="--suite memory"
    RUN_TAG="full"
    echo ">>> Mode: full (all memory)"
fi

COMMON_ARGS="$SUITE_ARGS --runs 1 -v --docker"

## Run
LOG_DATE=$(date +"%m%d")
LOG_DIR="./log/${LOG_DATE}"
mkdir -p "$LOG_DIR"

echo "========== memory test [${RUN_TAG}] (parallel) =========="
echo "Images (${#DOCKER_IMAGES[@]}): ${DOCKER_IMAGE_NAMES[*]}"
echo "Models (${#MODELS[@]}): ${MODEL_NAMES[*]}"
echo "Max parallel: ${MAX_PARALLEL:-unlimited}"
echo ""

for d in "${!DOCKER_IMAGES[@]}"; do
    DOCKER_IMG="${DOCKER_IMAGES[$d]}"
    DOCKER_TAG="${DOCKER_IMAGE_NAMES[$d]}"
    OUTPUT_DIR="results/${LOG_DATE}_${DOCKER_TAG}_memory_compare"

    echo "===== Image: ${DOCKER_TAG} (${DOCKER_IMG}) ====="

    for i in "${!MODELS[@]}"; do
        if [ "$MAX_PARALLEL" -gt 0 ] && [ $RUNNING -ge "$MAX_PARALLEL" ]; then
            wait_one
        fi
        TAG="${DOCKER_TAG}_${RUN_TAG}_${MODEL_NAMES[$i]}"
        LOG_FILE="$LOG_DIR/${TAG}.log"
        launch_task "$TAG" "$LOG_FILE" "$DOCKER_IMG" "./scripts/run.sh ${MODELS[$i]} $COMMON_ARGS --output-dir $OUTPUT_DIR"
    done
done

wait_all
