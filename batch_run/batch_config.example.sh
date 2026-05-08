#!/bin/bash
# =============================================================================
# Batch Run Configuration
# =============================================================================
#
# Copy this file to batch_config.sh and fill in your docker images and models:
#   cp batch_run/batch_config.example.sh batch_run/batch_config.sh
#
# This file is sourced by all batch_run/*.sh scripts.
# =============================================================================

# -----------------------------------------------------------------------------
# Docker Images
# -----------------------------------------------------------------------------
# List the Docker image tags you built with workflow_step_1_image_builder.sh.
# DOCKER_IMAGES: full image tag names
# DOCKER_IMAGE_NAMES: short display names (used in output dirs and logs)
#
# These two arrays must have the same length and correspond by index.

DOCKER_IMAGES=(
    "openclaw-official-v20260430_120000"
    # "openclaw-offical_shield-v20260430_120000"
    # "openclaw-offical_secureclaw-v20260430_120000"
    # "openclaw-offical_clawkeeper-v20260430_120000"
)
DOCKER_IMAGE_NAMES=(
    "official"
    # "shield"
    # "secureclaw"
    # "clawkeeper"
)

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
# List the models to evaluate (must match providers configured in config.yaml).
# Format: "--model <provider-id>/<model-id>"
#
# MODELS: array of --model flags
# MODEL_NAMES: short display names (used in logs and output filenames)
#
# These two arrays must have the same length and correspond by index.

MODELS=(
    "--model my-provider/model-a"
    "--model my-provider/model-b"
)
MODEL_NAMES=(
    "model-a"
    "model-b"
)
