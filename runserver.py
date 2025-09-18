# run_daphne_reload.py
"""Start Docker/Redis (if needed) and run Daphne with an auto-reloader that
watches multiple folders and file extensions. Cross-platform-ish.
"""
import os
import time
import subprocess
import sys
import platform
import shutil
import signal

# === CONFIG ===
DOCKER_REDIS_CONTAINER = "redis"    # <--- replace with your redis container name
DOCKER_REDIS_IMAGE = "redis:7"         # used only if container doesn't exist (fallback)
WATCHED_FOLDERS = ["tracker", "players", "static"]
WATCH_EXTENSIONS = (".py", ".html", ".css", ".js")
POLL_INTERVAL = 1.0  # seconds between scans
DAPHNE_CMD = ["daphne", "tracker.asgi:application"]
# ==============

def log(*args, **kwargs):
    print(time.strftime("[%H:%M:%S]"), *args, **kwargs)

def snapshot_files():
    """Return dict: path -> mtime for files in WATCHED_FOLDERS matching extensions."""
    snap = {}
    for folder in WATCHED_FOLDERS:
        if not os.path.exists(folder):
            continue
        for root, dirs, files in os.walk(folder):
            for fname in files:
                if fname.endswith(WATCH_EXTENSIONS):
                    path = os.path.join(root, fname)
                    try:
                        snap[path] = os.path.getmtime(path)
                    except FileNotFoundError:
                        pass
    return snap

def ensure_docker_running(timeout=30):
    """Try to ensure Docker engine is available. On Windows/Mac try to start Docker Desktop."""
    if shutil.which("docker") is None:
        log("Docker CLI not found on PATH. Skipping Docker checks.")
        return False

    def docker_ok():
        try:
            subprocess.run(["docker", "info"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False

    if docker_ok():
        return True

    log("Docker does not appear to be running. Attempting to start Docker Desktop (if present)...")
    system = platform.system()
    attempted = False

    if system == "Windows":
        possible = [
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            r"C:\Program Files\Docker\Docker Desktop\Docker Desktop.exe"
        ]
        for p in possible:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    attempted = True
                    log(f"Started Docker Desktop from: {p}")
                    break
                except Exception:
                    pass
    elif system == "Darwin":  # macOS
        possible = ["/Applications/Docker.app/Contents/MacOS/Docker"]
        for p in possible:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    attempted = True
                    log(f"Started Docker.app from: {p}")
                    break
                except Exception:
                    pass
    else:
        # On Linux it's dangerous to try to start docker programmatically (may need sudo).
        log("Running on Linux: please start the Docker daemon if it's not running.")
        attempted = False

    if not attempted:
        log("Couldn't auto-start Docker Desktop. Please start Docker manually.")
        # still wait a bit to allow user to start it
    # wait for docker to respond
    deadline = time.time() + timeout
    while time.time() < deadline:
        if docker_ok():
            log("Docker is running.")
            return True
        time.sleep(1)
    log("Docker did not become ready within timeout.")
    return False

def ensure_redis_running():
    """Ensure a redis container with name DOCKER_REDIS_CONTAINER is running.
    If not found, try to create it with docker run (fallback)."""
    if shutil.which("docker") is None:
        log("Docker CLI not available, cannot ensure Redis container.")
        return False

    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={DOCKER_REDIS_CONTAINER}", "--format", "{{.Names}} {{.Status}}"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()

    if not output:
        log(f"Redis container '{DOCKER_REDIS_CONTAINER}' not found. Attempting to create it with '{DOCKER_REDIS_IMAGE}'...")
        try:
            subprocess.run(["docker", "run", "-d", "--name", DOCKER_REDIS_CONTAINER, DOCKER_REDIS_IMAGE],
                           check=True)
            log("Redis container created and started.")
            return True
        except subprocess.CalledProcessError:
            log("Failed to create Redis container. Please create it (docker-compose or docker run) and retry.")
            return False

    # parse name and status
    try:
        name, status = output.split(maxsplit=1)
    except ValueError:
        # Unexpected format; try to start by name anyway
        name = DOCKER_REDIS_CONTAINER
        status = ""

    if "Up" in status:
        log(f"Redis container '{name}' is already running.")
        return True
    else:
        log(f"Starting existing Redis container '{name}' (status: {status})...")
        try:
            subprocess.run(["docker", "start", name], check=True)
            log("Redis started.")
            return True
        except subprocess.CalledProcessError:
            log("Failed to start existing Redis container.")
            return False

def start_daphne():
    """Start Daphne as a subprocess. Returns Popen instance."""
    log("Starting Daphne:", " ".join(DAPHNE_CMD))
    # DO NOT capture output so logs stream to your console
    proc = subprocess.Popen(DAPHNE_CMD)
    return proc

def stop_process(proc, timeout=5):
    if proc is None:
        return
    if proc.poll() is not None:
        return
    log("Stopping Daphne (pid=%s)..." % proc.pid)
    try:
        # Try graceful terminate first
        proc.terminate()
        proc.wait(timeout=timeout)
    except Exception:
        # force kill
        try:
            proc.kill()
            proc.wait(timeout=3)
        except Exception:
            pass
    log("Daphne stopped.")

def main():
    log("Booting dev reloader.")
    docker_ok = ensure_docker_running()
    if docker_ok:
        ensure_redis_running()
    else:
        log("Docker not running; skipping Redis auto-start (you can still use an external Redis).")

    last_snap = snapshot_files()
    log("Initial snapshot taken. Watching:", WATCHED_FOLDERS)
    daphne_proc = start_daphne()

    def shutdown(signum=None, frame=None):
        log("Shutting down (signal received).")
        stop_process(daphne_proc)
        sys.exit(0)

    # attach Ctrl-C handler
    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            new_snap = snapshot_files()
            changed = []
            # modified or added
            for path, m in new_snap.items():
                if path not in last_snap or last_snap[path] != m:
                    changed.append(("modified_or_added", path))
            # removed
            for path in list(last_snap.keys()):
                if path not in new_snap:
                    changed.append(("removed", path))

            if changed:
                # Pretty print and restart
                log("Change detected; restarting Daphne. Changes:")
                for kind, path in changed:
                    log("  ", kind, "->", path)
                # restart
                stop_process(daphne_proc)
                daphne_proc = start_daphne()
                # update snapshot after restart
                last_snap = new_snap
            else:
                # no changes; keep old snapshot
                pass
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
