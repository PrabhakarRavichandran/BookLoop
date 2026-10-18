"""
=============================================================
  BOOKLOOP - One-Click Launcher
  Run this file to start everything:
    * Sets up the MySQL database (first run only)
    * Kills any stale process on port 5000
    * Starts Flask on  http://localhost:5000
      (serves BOTH the API AND the frontend HTML files)
    * Opens http://localhost:5000 in your browser
=============================================================
  Usage:
      python run.py
=============================================================
"""

import os
import sys
import time
import signal
import socket
import subprocess
import webbrowser

# ─── Paths ────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
SCHEMA_SQL  = os.path.join(BACKEND_DIR, "schema.sql")
MYSQL_EXE   = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

# ─── Config ───────────────────────────────────────────────────
MYSQL_USER     = "root"
MYSQL_PASSWORD = "Prabhakar@2006"
MYSQL_DB       = "bookloop"
API_PORT       = 5000
OPEN_URL       = f"http://localhost:{API_PORT}"

# ─── Globals ──────────────────────────────────────────────────
_flask_proc = None

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def banner(text):
    width = 57
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def wait_for_port(port, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not port_free(port):
            return True
        time.sleep(0.3)
    return False


def kill_port(port):
    """Kill whatever process is listening on the given port (Windows)."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f":{port} " in line and "LISTENING" in line:
                parts = line.split()
                pid = int(parts[-1])
                if pid > 0:
                    subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                                   capture_output=True)
                    print(f"  (killed stale process PID {pid} on port {port})")
                    time.sleep(0.5)
    except Exception as e:
        print(f"  (could not clear port {port}: {e})")


def shutdown(sig=None, frame=None):
    global _flask_proc
    print("\n\n[Launcher] Shutting down BookLoop...", flush=True)
    if _flask_proc and _flask_proc.poll() is None:
        _flask_proc.terminate()
        try:
            _flask_proc.wait(timeout=5)
        except Exception:
            _flask_proc.kill()
    sys.exit(0)


# ─────────────────────────────────────────────────────────────
# STEP 1 - Ensure the database and tables exist
# ─────────────────────────────────────────────────────────────

def setup_database():
    print("[1/2] Checking MySQL database...", end=" ", flush=True)

    if not os.path.isfile(MYSQL_EXE):
        print(f"\n  ERROR: mysql.exe not found at:\n    {MYSQL_EXE}")
        print("  Update MYSQL_EXE in run.py to the correct path.")
        sys.exit(1)

    # Check if the bookloop DB + users table already has rows
    check_cmd = [
        MYSQL_EXE, "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}",
        MYSQL_DB, "-e", "SELECT COUNT(*) FROM users;"
    ]
    result = subprocess.run(check_cmd, capture_output=True, text=True)

    already_seeded = False
    if result.returncode == 0:
        try:
            count = int(result.stdout.strip().split("\n")[-1].strip())
            already_seeded = count > 0
        except Exception:
            pass

    if already_seeded:
        print("OK (data already present)")
        return

    # First run: create DB and run schema
    print("running schema...", end=" ", flush=True)
    subprocess.run(
        [MYSQL_EXE, "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}",
         "-e", f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"],
        capture_output=True
    )
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        schema = f.read()
    proc = subprocess.run(
        [MYSQL_EXE, "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}", MYSQL_DB],
        input=schema, capture_output=True, text=True
    )
    if proc.returncode != 0:
        print("FAILED")
        print("  stderr:", proc.stderr[:500])
        sys.exit(1)
    print("done (seeded 6 users + 8 books)")


# ─────────────────────────────────────────────────────────────
# STEP 2 - Start Flask  (API + frontend, single port 5000)
# ─────────────────────────────────────────────────────────────

def start_flask():
    global _flask_proc
    print(f"[2/2] Starting BookLoop server on port {API_PORT}...", end=" ", flush=True)

    # Clear any stale process holding the port
    if not port_free(API_PORT):
        print()
        kill_port(API_PORT)
        time.sleep(0.8)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    _flask_proc = subprocess.Popen(
        [sys.executable, os.path.join(BACKEND_DIR, "app.py"), "--no-reload"],
        cwd=BACKEND_DIR,
        env=env,
        # Stream output directly to our terminal so errors are visible
        stdout=None,
        stderr=None,
    )

    if wait_for_port(API_PORT, timeout=20):
        print("OK")
    else:
        print("TIMEOUT - Flask may not have started.")
        print("  Check the error output above, or run manually:")
        print(f"    python {os.path.join(BACKEND_DIR, 'app.py')}")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    banner("BookLoop  -  One-Click Launcher")
    print()

    setup_database()
    start_flask()

    print()
    banner(f"BookLoop is LIVE  ->  {OPEN_URL}")
    print()
    print("  Frontend + API both served on port 5000.")
    print("  Login with:  prabhakar@campus.edu  /  pass123")
    print()
    print("  Press  Ctrl+C  to stop.")
    print()

    # Open browser
    time.sleep(0.5)
    webbrowser.open(OPEN_URL)

    # Keep alive — watch Flask and restart if it crashes
    try:
        while True:
            if _flask_proc and _flask_proc.poll() is not None:
                code = _flask_proc.returncode
                print(f"\n[Launcher] Flask exited (code {code}). Restarting...", flush=True)
                time.sleep(2)
                start_flask()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
