"""
Cybercamp 2026 - staff bot
"""

import os
import re
import time
import queue
import threading
from urllib.parse import unquote, urlparse

import requests
from flask import Flask, jsonify, request

# config
APP_BASE_URL = os.environ.get("APP_BASE_URL").rstrip("/")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ALLOWED_HOSTS = {h.strip() for h in os.environ.get("ALLOWED_HOSTS").split(",") if h.strip()}
TIMEOUT = float(os.environ.get("VISIT_TIMEOUT"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS"))
QUEUE_MAX = int(os.environ.get("QUEUE_MAX"))

# staff session
session = requests.Session()
session.headers["User-Agent"] = "SrdnlenStaffBot/1.0"
_logged_in = False
_login_lock = threading.Lock()


def login():
    # login as staff
    global _logged_in
    with _login_lock:
        page = session.get(f"{APP_BASE_URL}/login", timeout=TIMEOUT)
        token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.text)
        data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        if token:
            data["csrf_token"] = token.group(1)
        resp = session.post(f"{APP_BASE_URL}/login", data=data, timeout=TIMEOUT, allow_redirects=False)
        _logged_in = resp.is_redirect


# url validation
def build_target(url):
    # normalize encoding before parsing
    parsed = urlparse(unquote((url or "").strip()))
    
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return None
    if parsed.netloc and parsed.netloc not in ALLOWED_HOSTS:
        return None
        
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{APP_BASE_URL}{parsed.path or '/'}{query}"


def visit(target):
    if not _logged_in:
        login()
    try:
        session.get(target, timeout=TIMEOUT, allow_redirects=False)
    except requests.RequestException:
        pass


# queue + worker pool
work_queue = queue.Queue(maxsize=QUEUE_MAX)


def worker():
    while True:
        target = work_queue.get()
        try:
            visit(target)
        except Exception:
            pass
        finally:
            work_queue.task_done()

# api
bot = Flask(__name__)


@bot.route("/health")
def health():
    return jsonify(status="ok")


@bot.route("/report", methods=["POST"])
def report():
    target = build_target((request.get_json(silent=True) or {}).get("url"))
    if target is None:
        return jsonify(status="rejected"), 400
    try:
        work_queue.put_nowait(target)
    except queue.Full:
        return jsonify(status="busy"), 503
    return jsonify(status="queued"), 202


# startup
def _startup_login():
    for _ in range(30):
        try:
            login()
            if _logged_in:
                return
        except requests.RequestException:
            pass
        time.sleep(1)


for _ in range(NUM_WORKERS):
    threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=_startup_login, daemon=True).start()


if __name__ == "__main__":
    bot.run(host="0.0.0.0", port=8080)
