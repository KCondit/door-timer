from flask import Flask, render_template, request, abort, jsonify
import os
import time
from datetime import datetime
import pytz

app = Flask(__name__)

# Simple in-memory store
door_state = "unknown"
timer = 0.0
API_KEY = os.environ.get("DOOR_API_KEY", "changeme")

# For session logging
session_log = []
current_session_start = None
previous_state = None

def format_duration(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes != 1 else ''}, {secs} second{'s' if secs != 1 else ''}"
    else:
        return f"{secs} second{'s' if secs != 1 else ''}"

def format_date(ts):
    # Display in Hawaii time
    tz = pytz.timezone('Pacific/Honolulu')
    dt = datetime.fromtimestamp(ts, tz)
    # For platforms that don't support %-d or %-I, just use %d and %I (may have leading zeros)
    return dt.strftime('%B %-d, %Y at %-I:%M%p HST') if hasattr(dt, 'strftime') else dt.strftime('%B %d, %Y at %I:%M%p HST')

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        door_state=door_state,
        timer=int(float(timer)),
        session_log=session_log[::-1],  # Show most recent first
    )

@app.route("/update", methods=["POST"])
def update():
    if request.form.get("api_key") != API_KEY:
        abort(403)
    global door_state, timer, session_log, current_session_start, previous_state

    new_state = request.form.get("door_state", "unknown")
    try:
        new_timer = float(request.form.get("timer", 0.0))
    except ValueError:
        new_timer = 0.0

    now = time.time()
    print("PREV STATE:", previous_state, "NEW STATE:", new_state)
    print("current_session_start:", current_session_start)
    if previous_state is not None:
        # Start of session (door just closed)
        if previous_state == "open" and new_state == "closed":
            print("Session STARTED at", now)
            current_session_start = now
        # End of session (door just opened)
        elif previous_state == "closed" and new_state == "open" and current_session_start is not None:
            print("Session ENDED at", now)
            duration_secs = int(now - current_session_start)
            session = {
                "start": format_date(current_session_start),
                "end": format_date(now),
                "duration": format_duration(duration_secs)
            }
            session_log.append(session)
            del session_log[:-50]  # Keep last 50
            print("Session LOGGED:", session)
            current_session_start = None

    previous_state = new_state
    door_state = new_state
    timer = new_timer
    return "OK"

@app.route("/status", methods=["GET"])
def status():
    return jsonify(door_state=door_state, timer=int(float(timer)))

@app.route("/sessions", methods=["GET"])
def sessions():
    return jsonify(session_log=session_log[::-1])  # Most recent first

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
