#!/bin/bash
# ---------------------------------------------------------------------------
# 2.sync_naukri_file.sh  (Naukri equivalent of 2.sync_ats_file.sh)
#
# Copies the LATEST code files from naukri1 into every other naukri<i> folder
# and re-applies rank = i and total_scripts = <number of folders>. Runtime files
# (state, output, logs, queues) in the targets are never touched.
# Run this after editing find_naukri_job.py (or a helper module) in naukri1.
# ---------------------------------------------------------------------------
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

SOURCE_FOLDER="naukri1"
PYTHON_FILE="find_naukri_job.py"
SYNC_FILES=("$PYTHON_FILE" new_mylib.py target_audience_roles.py save_naukri_login.py naukri_auth.json)
FOLDER_PREFIX="naukri"

if [ ! -f "$SOURCE_FOLDER/$PYTHON_FILE" ]; then
    echo "Error: $SOURCE_FOLDER/$PYTHON_FILE not found."
    exit 1
fi

FOLDERS=()
for d in "$FOLDER_PREFIX"[0-9]*/; do
    [ -d "$d" ] && FOLDERS+=("${d%/}")
done
TOTAL="${#FOLDERS[@]}"          # includes naukri1

SOURCE_NUM_SYS="$(sed -n 's/^total_scripts *= *\([0-9]\+\).*/\1/p' "$SOURCE_FOLDER/$PYTHON_FILE" | head -1)"
if [ "$SOURCE_NUM_SYS" != "$TOTAL" ]; then
    echo "total_scripts in $SOURCE_FOLDER is $SOURCE_NUM_SYS but $TOTAL folders exist; setting total_scripts = $TOTAL."
    sed -i "s/^total_scripts *= *.*/total_scripts = $TOTAL/" "$SOURCE_FOLDER/$PYTHON_FILE"
fi
sed -i "s/^rank *= *.*/rank = 1/" "$SOURCE_FOLDER/$PYTHON_FILE"

for folder in "${FOLDERS[@]}"; do
    [ "$folder" = "$SOURCE_FOLDER" ] && continue
    i="${folder#$FOLDER_PREFIX}"
    echo "Updating $folder ..."
    for f in "${SYNC_FILES[@]}"; do
        [ -f "$SOURCE_FOLDER/$f" ] && cp "$SOURCE_FOLDER/$f" "$folder/"
    done
    rm -rf "$folder/__pycache__"
    sed -i "s/^rank *= *.*/rank = $i/" "$folder/$PYTHON_FILE"
    sed -i "s/^total_scripts *= *.*/total_scripts = $TOTAL/" "$folder/$PYTHON_FILE"
    echo "$folder/$PYTHON_FILE updated with rank = $i, total_scripts = $TOTAL"
done

echo "All files synced successfully from $SOURCE_FOLDER into $((TOTAL - 1)) folder(s)."
