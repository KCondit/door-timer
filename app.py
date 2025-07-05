from flask import Flask, render_template, request, abort, jsonify
import os
from datetime import datetime
from collections import deque

app = Flask(__name__)

# Simple in-memory store
door_state = "unknown"
timer = 0.0
API_KEY = os.environ.get("DOOR_API_KEY", "changeme")

# Session tracking
previous_state = door_state  # Initialize to current state
current_session_start = None
session_log = deque(maxlen=50)  # Keep last 50 sessions

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        door_state=door_state,
        timer=int(float(timer)),
        session_log=list(session_log)
    )

@app.route("/update", methods=["POST"])
def update():
    if request.form.get("api_key") != API_KEY:
        abort(403)
    global door_state, timer, previous_state, current_session_start
    
    new_state = request.form.get("door_state", "unknown")
    try:
        timer = float(request.form.get("timer", 0.0))
    except ValueError:
        timer = 0.0
    
    # Track session transitions
    if previous_state != new_state:
        # Session starts when door becomes closed
        if new_state == "closed" and previous_state != "closed":
            current_session_start = datetime.now()
        
        # Session ends when door changes from closed to open
        elif previous_state == "closed" and new_state == "open":
            if current_session_start:
                session_end = datetime.now()
                duration = session_end - current_session_start
                
                # Add session to log
                session_log.append({
                    'start': current_session_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'end': session_end.strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': str(duration).split('.')[0]  # Remove microseconds
                })
                current_session_start = None
    
    previous_state = new_state
    door_state = new_state
    return "OK"

@app.route("/status", methods=["GET"])
def status():
    return jsonify(door_state=door_state, timer=int(float(timer)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
