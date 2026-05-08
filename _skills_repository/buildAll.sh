#!/bin/bash

# buildAll.sh - Package all skills and copy them to the target directory
# Usage: ./buildAll.sh [target directory]
# If no target directory is specified, use ../_skills_repository/skill_dest by default

set -e

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_REPO_DIR="${SCRIPT_DIR}"

# Target directory: prefer the argument, otherwise use the default
if [[ -n "$1" ]]; then
    SKILL_DEST="$1"
else
    SKILL_DEST="${SKILLS_REPO_DIR}/../_skills_repository/skill_dest"
fi

# Ensure the target directory is an absolute path
SKILL_DEST="$(cd "$(dirname "${SKILL_DEST}")" 2>/dev/null && pwd)/$(basename "${SKILL_DEST}")" || {
    # If the directory does not exist, create its parents
    mkdir -p "${SKILL_DEST}"
    SKILL_DEST="$(cd "${SKILL_DEST}" && pwd)"
}

echo "=========================================="
echo "Packaging skills..."
echo "Source directory: ${SKILLS_REPO_DIR}"
echo "Target directory: ${SKILL_DEST}"
echo "=========================================="

# Create target directories
mkdir -p "${SKILL_DEST}/skills"
mkdir -p "${SKILL_DEST}/skill_data"

# Iterate over all skill directories
skill_count=0
for skill_dir in "${SKILLS_REPO_DIR}"/*/; do
    # Skip non-directories
    if [[ ! -d "${skill_dir}" ]]; then
        continue
    fi

    skill_name=$(basename "${skill_dir}")

    # Skip non-skill directories such as __pycache__
    if [[ "${skill_name}" == "__pycache__" ]] || [[ "${skill_name}" == .* ]]; then
        continue
    fi

    # Check whether this is a valid skill directory with SKILL.md or skill.md
    if [[ ! -f "${skill_dir}SKILL.md" ]] && [[ ! -f "${skill_dir}skill.md" ]]; then
        echo "  Skipping non-skill directory: ${skill_name}"
        continue
    fi

    echo ""
    echo "Processing skill: ${skill_name}"
    skill_count=$((skill_count + 1))

    # Run build scripts for both Mac and Linux
    build_mac="${skill_dir}build_mac.sh"
    build_linux="${skill_dir}build_linux.sh"

    # Build Mac version
    if [[ -f "${build_mac}" ]]; then
        echo "  Running build script: $(basename "${build_mac}")"
        (cd "${skill_dir}" && bash "$(basename "${build_mac}")")
    else
        echo "  Warning: build script not found: ${build_mac}"
    fi

    # Build Linux version
    if [[ -f "${build_linux}" ]]; then
        echo "  Running build script: $(basename "${build_linux}")"
        (cd "${skill_dir}" && bash "$(basename "${build_linux}")")
    else
        echo "  Warning: build script not found: ${build_linux}"
    fi

    # Create target skill directory
    dest_skill_dir="${SKILL_DEST}/skills/${skill_name}"
    mkdir -p "${dest_skill_dir}"

    # Copy skill directory contents
    echo "  Copying files..."
    cp -r "${skill_dir}"* "${dest_skill_dir}/"

    # Extract the data directory into skill_data before cleanup
    # Use -E for extended regular expressions in macOS BSD sed
    skill_name_no_version=$(echo "${skill_name}" | sed -E 's/-[0-9]+\.[0-9]+\.[0-9]+$//')
    if [[ -d "${dest_skill_dir}/data" ]]; then
        echo "  Extracting data -> skill_data/${skill_name_no_version}/data/"
        mkdir -p "${SKILL_DEST}/skill_data/${skill_name_no_version}/data/"
        cp -r "${dest_skill_dir}/data/"* "${SKILL_DEST}/skill_data/${skill_name_no_version}/data/"
    fi

    # Clean generated files from the skill directory and keep only required files
    echo "  Cleaning generated files..."
    for item in "${dest_skill_dir}/"*; do
        if [[ ! -e "${item}" ]]; then
            continue
        fi

        item_name=$(basename "${item}")

        # Decide whether to keep this item
        keep=false

        # Keep directory: scripts. config is hardcoded in main.py and no longer needed.
        if [[ -d "${item}" ]]; then
            if [[ "${item_name}" == "scripts" ]]; then
                keep=true
            fi
        # Keep file: SKILL.md, case-insensitive
        elif [[ "$(echo "${item_name}" | tr '[:upper:]' '[:lower:]')" == "skill.md" ]]; then
            keep=true
        # Keep executable binaries, excluding script files such as .sh or .py
        elif [[ -x "${item}" ]]; then
            # Exclude script files and hidden files
            case "${item_name}" in
                *.sh|*.py|*.rb|*.pl|*.lua) ;;
                .*) ;;
                *) keep=true ;;
            esac
        fi

        # Remove files/directories that should not be kept
        if [[ "${keep}" == "false" ]]; then
            rm -rf "${item}"
        fi
    done

    # Remove hidden files such as .DS_Store
    find "${dest_skill_dir}" -maxdepth 1 -name ".*" -type f -delete 2>/dev/null || true

    echo "  Done: ${skill_name}"
done

echo ""
echo "=========================================="
echo "Packaging complete!"
echo "Processed ${skill_count} skills"
echo "Target directory: ${SKILL_DEST}"
echo "  - skills/     : packaged skill directories"
echo "  - skill_data/ : extracted data directories"
echo "=========================================="

# Copy skill_data into the assets directory
ASSETS_DIR="${SKILLS_REPO_DIR}/../assets"
if [[ -d "${SKILL_DEST}/skill_data" ]]; then
    echo ""
    echo "Copying skill_data to assets directory..."
    mkdir -p "${ASSETS_DIR}"
    rm -rf "${ASSETS_DIR}/skill_data"
    cp -r "${SKILL_DEST}/skill_data" "${ASSETS_DIR}/"
    echo "  Copied to: ${ASSETS_DIR}/skill_data"
fi
