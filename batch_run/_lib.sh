#!/bin/bash
# Shared parallel execution library for batch_run scripts.
# Source this file after setting DOCKER_IMAGES, MODELS, ATTACKS, etc.

launch_task() {
    local tag="$1"
    local log_file="$2"
    local docker_image="$3"
    shift 3
    echo "[$(date '+%H:%M:%S')] Starting: ${tag} -> ${log_file}"
    DOCKER_IMAGE="$docker_image" eval "$@" > "$log_file" 2>&1 &
    PIDS+=($!)
    TAGS+=("$tag")
    RUNNING=$((RUNNING + 1))
    TOTAL=$((TOTAL + 1))
}

wait_one() {
    local finished=0
    while [ $finished -eq 0 ] && [ ${#PIDS[@]} -gt 0 ]; do
        for k in "${!PIDS[@]}"; do
            if ! kill -0 "${PIDS[$k]}" 2>/dev/null; then
                wait "${PIDS[$k]}"
                local exit_code=$?
                if [ $exit_code -eq 0 ]; then
                    echo "[$(date '+%H:%M:%S')] Done: ${TAGS[$k]}"
                else
                    echo "[$(date '+%H:%M:%S')] Failed: ${TAGS[$k]} (exit=$exit_code)"
                    FAIL=$((FAIL + 1))
                fi
                unset 'PIDS[k]'
                unset 'TAGS[k]'
                PIDS=("${PIDS[@]}")
                TAGS=("${TAGS[@]}")
                RUNNING=$((RUNNING - 1))
                finished=1
                break
            fi
        done
        [ $finished -eq 0 ] && sleep 1
    done
}

wait_all() {
    echo ""
    echo "[$(date '+%H:%M:%S')] All tasks dispatched, waiting for ${#PIDS[@]} remaining..."
    echo ""
    for k in "${!PIDS[@]}"; do
        if wait "${PIDS[$k]}"; then
            echo "[$(date '+%H:%M:%S')] Done: ${TAGS[$k]}"
        else
            echo "[$(date '+%H:%M:%S')] Failed: ${TAGS[$k]} (exit=$?)"
            FAIL=$((FAIL + 1))
        fi
    done
    echo ""
    echo "========== Complete [${RUN_TAG}] (failed: $FAIL/$TOTAL) =========="
}

# Load and validate shared config
load_batch_config() {
    local script_dir="$1"

    if [[ ! -f "${script_dir}/../env.sh" ]]; then
        echo "[ERROR] env.sh not found. Run 'bash setup.sh' first."
        exit 1
    fi
    source "${script_dir}/../env.sh"

    if [[ ! -f "${script_dir}/batch_config.sh" ]]; then
        echo "[ERROR] batch_run/batch_config.sh not found."
        echo "  cp batch_run/batch_config.example.sh batch_run/batch_config.sh"
        echo "  Then edit it with your docker images and models."
        exit 1
    fi
    source "${script_dir}/batch_config.sh"

    if [[ ${#DOCKER_IMAGES[@]} -eq 0 ]]; then
        echo "[ERROR] DOCKER_IMAGES is empty in batch_config.sh"
        exit 1
    fi
    if [[ ${#MODELS[@]} -eq 0 ]]; then
        echo "[ERROR] MODELS is empty in batch_config.sh"
        exit 1
    fi
    if [[ ${#DOCKER_IMAGES[@]} -ne ${#DOCKER_IMAGE_NAMES[@]} ]]; then
        echo "[ERROR] DOCKER_IMAGES and DOCKER_IMAGE_NAMES must have the same length"
        exit 1
    fi
    if [[ ${#MODELS[@]} -ne ${#MODEL_NAMES[@]} ]]; then
        echo "[ERROR] MODELS and MODEL_NAMES must have the same length"
        exit 1
    fi
}

# Initialize parallel state
init_parallel() {
    MAX_PARALLEL="${MAX_PARALLEL:-0}"
    PIDS=()
    TAGS=()
    RUNNING=0
    FAIL=0
    TOTAL=0
}
