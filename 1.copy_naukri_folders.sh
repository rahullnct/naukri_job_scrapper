#!/bin/bash
# ---------------------------------------------------------------------------
# 1.copy_naukri_folders.sh  (Naukri equivalent of 1.copy_ats_folders.sh)
#
# naukri1 is the source, exactly like ats1. This script creates naukri2..naukriN
# as copies of naukri1 and sets in every folder (naukri1 included):
#     rank    = <folder number>
#     total_scripts = <N>
# so the city list is split evenly across all N workers.
#
# Usage:   ./1.copy_naukri_folders.sh [N]        (default N = total_scripts in naukri1)
#
# Runtime files (state_*.json, cycle_state*.json, *.xlsx, *.log, 5xx queues)
# are NOT copied from naukri1, and a target folder's own runtime files are
# kept when it is recreated, so no rank ever inherits another rank's state.
# ---------------------------------------------------------------------------
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

SOURCE_FOLDER="naukri1"
PYTHON_FILE="find_naukri_job.py"
FOLDER_PREFIX="naukri"

if [ ! -d "$SOURCE_FOLDER" ]; then
    echo "Error: $SOURCE_FOLDER folder not found."
    exit 1
fi
if [ ! -f "$SOURCE_FOLDER/$PYTHON_FILE" ]; then
    echo "Error: $SOURCE_FOLDER/$PYTHON_FILE not found."
    exit 1
fi
if [ ! -f "$SOURCE_FOLDER/naukri_auth.json" ]; then
    echo "Error: $SOURCE_FOLDER/naukri_auth.json not found. Run save_naukri_login.py first."
    exit 1
fi

SOURCE_NUM_SYS="$(sed -n 's/^total_scripts *= *\([0-9]\+\).*/\1/p' "$SOURCE_FOLDER/$PYTHON_FILE" | head -1)"
TOTAL="${1:-${SOURCE_NUM_SYS:-5}}"
if ! [[ "$TOTAL" =~ ^[0-9]+$ ]] || [ "$TOTAL" -lt 1 ]; then
    echo "Error: N must be a positive integer (got '$TOTAL')."
    exit 1
fi

# Per-rank runtime files (never copied between folders).
is_runtime_file() {
    case "$1" in
        state_*.json|cycle_state*.json|naukri_5xx_unresolved*.json|\
        naukri_access_events*.log|*.xlsx|*.log|__pycache__) return 0 ;;
        *) return 1 ;;
    esac
}

# Source keeps rank 1 and gets the matching total_scripts.
sed -i "s/^rank *= *.*/rank = 1/" "$SOURCE_FOLDER/$PYTHON_FILE"
sed -i "s/^total_scripts *= *.*/total_scripts = $TOTAL/" "$SOURCE_FOLDER/$PYTHON_FILE"
echo "$SOURCE_FOLDER: rank = 1, total_scripts = $TOTAL"

for i in $(seq 2 "$TOTAL"); do
    TARGET="${FOLDER_PREFIX}$i"
    echo "Creating $TARGET..."

    # Keep the target's own runtime files across a re-copy.
    KEEP_DIR="$(mktemp -d)"
    if [ -d "$TARGET" ]; then
        for f in "$TARGET"/*; do
            [ -e "$f" ] || continue
            name="$(basename "$f")"
            if is_runtime_file "$name" && [ "$name" != "__pycache__" ]; then mv "$f" "$KEEP_DIR/"; fi
        done
        rm -rf "$TARGET"
    fi
    mkdir -p "$TARGET"

    # Copy naukri1 minus its runtime files.
    for f in "$SOURCE_FOLDER"/*; do
        [ -e "$f" ] || continue
        name="$(basename "$f")"
        is_runtime_file "$name" && continue
        cp -r "$f" "$TARGET/"
    done

    mv "$KEEP_DIR"/* "$TARGET/" 2>/dev/null || true
    rmdir "$KEEP_DIR"

    sed -i "s/^rank *= *.*/rank = $i/" "$TARGET/$PYTHON_FILE"
    sed -i "s/^total_scripts *= *.*/total_scripts = $TOTAL/" "$TARGET/$PYTHON_FILE"
    echo "$TARGET created with rank = $i, total_scripts = $TOTAL"
done

echo "All folders created successfully from ${FOLDER_PREFIX}2 to ${FOLDER_PREFIX}$TOTAL."
