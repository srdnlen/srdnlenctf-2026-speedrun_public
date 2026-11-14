import os
import json
import time
import threading
from functools import wraps

import requests
from flask import Flask, flash, g, redirect, render_template, request, session
from flask_wtf.csrf import CSRFProtect

from utils import RateLimiter, hash_password, verify_password

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

CSRFProtect(app)

FLAG = os.environ.get("FLAG")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
BOT_URL = os.environ.get("BOT_URL")

if not all([app.config["SECRET_KEY"], ADMIN_USERNAME, ADMIN_PASSWORD, FLAG, BOT_URL]):
    raise RuntimeError("Missing required environment variables.")

MAX_PASSWORD = 8
RATE_LIMIT = 2
limiter = RateLimiter(RATE_LIMIT)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
with open(os.path.join(DATA_DIR, "challenges.json"), encoding="utf-8") as _f:
    _data = json.load(_f)
CATEGORIES = _data["categories"]
CHALLENGES = _data["challenges"]
CHALLENGE_BY_ID = {c["id"]: c for c in CHALLENGES}

# memory
lock = threading.Lock()
users = {}
reviewers = set()
reports = []
# ------

with lock:
    users[ADMIN_USERNAME] = hash_password(ADMIN_PASSWORD)
    reviewers.add(ADMIN_USERNAME)

app.jinja_env.globals["reviewers"] = reviewers

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        username = session.get("username")
        with lock:
            exists = username in users
        if not exists:
            session.pop("username", None)
            return redirect("/login")
        g.username = username
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    grouped = [(cat, [c for c in CHALLENGES if c["category"] == cat]) for cat in CATEGORIES]
    return render_template("home.html", grouped=grouped)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")
    
    if limiter.hit(f"register:{request.remote_addr}"):
        return render_template("register.html", error="Too many attempts, slow down.")
    
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if (not username or not password or any(c.isspace() for c in username)
            or len(username) > 32 or len(password) > MAX_PASSWORD):
        return render_template("register.html", error="Invalid username or password.")
    
    with lock:
        if username in users:
            return render_template("register.html", error="That username is already taken.")
        users[username] = hash_password(password)

    session["username"] = username

    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")
    
    if limiter.hit(f"login:{request.remote_addr}"):
        return render_template("login.html", error="Too many attempts, slow down.")
    
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    with lock:
        stored = users.get(username)

    if stored and len(password) <= 128 and verify_password(stored, password):
        session["username"] = username
        return redirect("/")
    
    return render_template("login.html", error="Invalid credentials.")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")


@app.route("/challenge/<cid>")
def challenge(cid):
    ch = CHALLENGE_BY_ID.get(cid)

    if ch is None:
        return redirect("/")
    
    return render_template("challenge.html", ch=ch)


@app.route("/report", methods=["GET", "POST"])
@login_required
def report():

    if request.method == "GET":
        return render_template("report.html")
    if limiter.hit(f"report:{g.username}"):
        flash("Too many reports, wait a moment and try again.", "err")
        return redirect("/report")
    
    url = (request.form.get("url") or "").strip()

    if not url:
        flash("Paste the challenge URL.", "err")
        return redirect("/report")
    if "?" in url:
        flash("Only clean links are accepted.", "err")
        return redirect("/report")
    
    with lock:
        reports.append({"link": url, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        del reports[:-100]
    try:
        requests.post(f"{BOT_URL}/report", json={"url": url}, timeout=4)
    except requests.RequestException:
        pass

    flash("Report received. The staff will review the link as soon as possible.", "ok")

    return redirect("/report")


@app.route("/set_reviewer", methods=["POST", "GET"])
def set_reviewer():

    if session.get("username") == ADMIN_USERNAME:
        user = request.values.get("user")
        if user:
            with lock:
                reviewers.add(user)

    return redirect("/reviews")


@app.route("/reviews")
@login_required
def reviews():

    with lock:
        unlocked = g.username in reviewers
        items = list(reversed(reports)) if unlocked else []

    return render_template("reviews.html", unlocked=unlocked, flag=FLAG if unlocked else None, reports=items, username=g.username)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
