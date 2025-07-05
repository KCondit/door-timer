from flask import Flask, render_template, request, abort, jsonify
import os
import time

app = Flask(__name__)

# Simple in-memory store
door_state = "unknown"
timer = 0.0
API_KEY = os.environ.get("DOOR_API_KEY", "changeme")

# For session logging
session_log = []  # Each entry: {'start': ..., 'end': ..., 'duration': ...}
current_session_start = None
previous_state = None

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        door_state=door_state,
        timer=int(float(timer)),
        session_log=session_log[::-1]  # Show most recent first
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

    # Detect transitions for session logging
    now = time.time()
    if previous_state is not None:
        # Start of session
        if previous_state == "open" and new_state == "closed":
            current_session_start = now
        # End of session: add to log
        elif previous_state == "closed" and new_state == "open" and current_session_start is not None:
            session = {
                "start": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_session_start)),
                "end": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now)),
                "duration": int(now - current_session_start)
            }
            session_log.append(session)
            # Keep only last 50
            del session_log[:-50]
            current_session_start = None
    previous_state = new_state

    door_state = new_state
    timer = new_timer
    return "OK"

@app.route("/status", methods=["GET"])
def status():
    return jsonify(door_state=door_state, timer=int(float(timer)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
