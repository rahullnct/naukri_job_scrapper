#!/bin/bash
# ---------------------------------------------------------------------------
# launch_naukri.sh  (Naukri equivalent of launch_ats.sh)
#
# Opens one terminal per naukri<i> folder and runs find_naukri_job.py in it.
# Any key in this launcher, or Ctrl+C in this or any worker terminal, stops
# every worker. PIDs are tracked in .naukri_pids.
#
#   NAUKRI_NO_TERMINAL=1 ./launch_naukri.sh   -> run in background, log to
#                                                naukri<i>/naukri<i>.log
# ---------------------------------------------------------------------------

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="find_naukri_job.py"
FOLDER_PREFIX="naukri"

FOLDERS=()
for d in "$BASE_DIR/$FOLDER_PREFIX"[0-9]*/; do
    [ -d "$d" ] && FOLDERS+=("$(basename "$d")")
done
if [ "${#FOLDERS[@]}" -eq 0 ]; then
    echo "[ERROR] No ${FOLDER_PREFIX}<n> folders found. Run ./1.copy_naukri_folders.sh first."
    exit 1
fi

# Remove state files that carry the WRONG rank suffix (e.g. a rank-1 file
# inside naukri3). A folder's own rank files are never deleted.
for folder in "${FOLDERS[@]}"; do
    own="${folder#$FOLDER_PREFIX}"
    for f in "$BASE_DIR/$folder"/state_city_*.json "$BASE_DIR/$folder"/state_role_*.json \
             "$BASE_DIR/$folder"/cycle_state_*.json "$BASE_DIR/$folder"/state_5xx_*_*.json \
             "$BASE_DIR/$folder"/naukri_5xx_unresolved_*.json \
             "$BASE_DIR/$folder"/naukri_access_events_*.log; do
        [ -e "$f" ] || continue
        suffix="$(basename "$f")"; suffix="${suffix%.*}"; suffix="${suffix##*_}"
        if [[ "$suffix" =~ ^[0-9]+$ ]] && [ "$suffix" != "$own" ]; then
            rm -f "$f" && echo "[CLEAN] removed $folder/$(basename "$f") (rank $suffix file in rank $own folder)"
        fi
    done
done

PID_DIR="$BASE_DIR/.naukri_pids"
STOPPING=0
CONTROLLER_PID=$$
mkdir -p "$PID_DIR"

# Python: the project venv first, then an active venv, then python3.
if [ -x "$BASE_DIR/venv/bin/python" ]; then
    PYTHON_EXECUTABLE="$BASE_DIR/venv/bin/python"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_EXECUTABLE="$VIRTUAL_ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_EXECUTABLE="$(command -v python3)"
else
    echo "[ERROR] Python was not found."
    exit 1
fi

if ! command -v setsid >/dev/null 2>&1; then
    echo "[ERROR] The setsid command was not found."
    exit 1
fi

echo "Using Python: $PYTHON_EXECUTABLE"

if ! "$PYTHON_EXECUTABLE" -c "import playwright, pandas, openpyxl" >/dev/null 2>&1; then
    echo "[ERROR] Required Python packages are missing."
    echo "Run:"
    echo "$PYTHON_EXECUTABLE -m pip install -r requirements.txt && $PYTHON_EXECUTABLE -m playwright install chromium"
    exit 1
fi

for folder in "${FOLDERS[@]}"; do
    if [ ! -f "$BASE_DIR/$folder/naukri_auth.json" ]; then
        echo "[WARNING] $folder/naukri_auth.json missing — that worker will stop at start."
    fi
done

# Refuse to start if an earlier launch is still running.
for pid_file in "$PID_DIR"/*.pid; do
    [ -e "$pid_file" ] || continue
    old_pid="$(cat "$pid_file" 2>/dev/null)"
    if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
        echo "[ERROR] A Naukri script is already running with PID $old_pid."
        echo "Stop the existing launcher before starting another one."
        exit 1
    fi
    rm -f "$pid_file"
done

stop_all() {
    if [ "$STOPPING" -eq 1 ]; then return; fi
    STOPPING=1
    echo
    echo "Stopping all Naukri scripts..."
    local running_pids=()
    for pid_file in "$PID_DIR"/*.pid; do
        [ -e "$pid_file" ] || continue
        pid="$(cat "$pid_file" 2>/dev/null)"
        if [[ "$pid" =~ ^[0-9]+$ ]]; then
            running_pids+=("$pid")
            kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    # Playwright needs a moment to close Chromium and flush the state files.
    sleep 3
    for pid in "${running_pids[@]}"; do
        kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
    done
    rm -f "$PID_DIR"/*.pid
    echo "All Naukri scripts have been stopped."
}

trap 'stop_all; exit 130' INT TERM      # Ctrl+C in the launcher terminal
trap 'stop_all; exit 0' USR1            # Ctrl+C in a worker terminal
trap 'stop_all' EXIT                    # launcher exits unexpectedly

if [ -n "${NAUKRI_NO_TERMINAL:-}" ]; then
    TERMINAL=""
elif command -v gnome-terminal >/dev/null 2>&1; then
    TERMINAL="gnome-terminal"
elif command -v konsole >/dev/null 2>&1; then
    TERMINAL="konsole"
elif command -v xterm >/dev/null 2>&1; then
    TERMINAL="xterm"
elif command -v x-terminal-emulator >/dev/null 2>&1; then
    TERMINAL="x-terminal-emulator"
else
    TERMINAL=""
fi

read -r -d '' CHILD_COMMAND <<'CHILD_SCRIPT'
folder_path="$1"
script_name="$2"
python_executable="$3"
pid_file="$4"
controller_pid="$5"

cd "$folder_path" || exit 1

notify_controller() {
    kill -USR1 "$controller_pid" 2>/dev/null || true
}
trap notify_controller INT TERM

setsid "$python_executable" "$script_name" &
python_pid=$!
printf "%s\n" "$python_pid" > "$pid_file"

wait "$python_pid"
exit_status=$?
rm -f "$pid_file"

echo
echo "Naukri process ended with status: $exit_status"
echo "You may close this terminal."
exec bash
CHILD_SCRIPT

launch_in_terminal() {
    local folder="$1"
    local folder_path="$BASE_DIR/$folder"
    local script_path="$folder_path/$SCRIPT_NAME"
    local pid_file="$PID_DIR/$folder.pid"

    if [ ! -f "$script_path" ]; then
        echo "[WARNING] Script not found: $script_path — skipping"
        return
    fi
    rm -f "$pid_file"

    case "$TERMINAL" in
        gnome-terminal)
            gnome-terminal --title="Naukri $folder" \
                -- bash -c "$CHILD_COMMAND" bash \
                "$folder_path" "$SCRIPT_NAME" "$PYTHON_EXECUTABLE" "$pid_file" "$CONTROLLER_PID"
            ;;
        konsole)
            konsole --title "Naukri $folder" \
                -e bash -c "$CHILD_COMMAND" bash \
                "$folder_path" "$SCRIPT_NAME" "$PYTHON_EXECUTABLE" "$pid_file" "$CONTROLLER_PID" &
            ;;
        xterm)
            xterm -T "Naukri $folder" \
                -e bash -c "$CHILD_COMMAND" bash \
                "$folder_path" "$SCRIPT_NAME" "$PYTHON_EXECUTABLE" "$pid_file" "$CONTROLLER_PID" &
            ;;
        x-terminal-emulator)
            x-terminal-emulator \
                -e bash -c "$CHILD_COMMAND" bash \
                "$folder_path" "$SCRIPT_NAME" "$PYTHON_EXECUTABLE" "$pid_file" "$CONTROLLER_PID" &
            ;;
    esac

    for _ in {1..50}; do
        [ -f "$pid_file" ] && break
        sleep 0.1
    done
    if [ -f "$pid_file" ]; then
        echo "[LAUNCHED] $folder | PID: $(cat "$pid_file")"
    else
        echo "[WARNING] $folder was opened, but its PID was not received."
    fi
}

launch_without_terminal() {
    local folder="$1"
    local folder_path="$BASE_DIR/$folder"
    local script_path="$folder_path/$SCRIPT_NAME"
    local pid_file="$PID_DIR/$folder.pid"
    local log_file="$folder_path/${folder}.log"

    if [ ! -f "$script_path" ]; then
        echo "[WARNING] Script not found: $script_path — skipping"
        return
    fi
    (
        cd "$folder_path" || exit 1
        setsid "$PYTHON_EXECUTABLE" "$SCRIPT_NAME" >"$log_file" 2>&1 &
        python_pid=$!
        printf "%s\n" "$python_pid" > "$pid_file"
    )
    echo "[LAUNCHED] $folder | PID: $(cat "$pid_file") | Log: $log_file"
}

for folder in "${FOLDERS[@]}"; do
    if [ -n "$TERMINAL" ]; then
        launch_in_terminal "$folder"
    else
        launch_without_terminal "$folder"
    fi
    # Stagger starts so the workers do not hit Naukri at the same instant.
    sleep 2
done

echo
echo "All available Naukri scripts have been launched (${#FOLDERS[@]} worker(s))."
echo "Press any key in this launcher terminal to stop all scripts."
echo "You can also press Ctrl+C in this terminal or any Naukri terminal."

IFS= read -rsn1
stop_all
trap - EXIT INT TERM USR1
exit 0
