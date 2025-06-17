from flask import Flask, request, render_template_string, abort
import os

app = Flask(__name__)

# Simple in-memory store
door_state = "unknown"
timer = 0.0

# Set this to something secret
API_KEY = os.environ.get("DOOR_API_KEY", "changeme")

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
        <h1>Door Timer</h1>
        <p>Door state: <b>{{ door_state }}</b></p>
        <p>Timer: <b>{{ timer }} seconds</b></p>
    """, door_state=door_state, timer=timer)

@app.route("/update", methods=["POST"])
def update():
    if request.form.get("api_key") != API_KEY:
        abort(403)
    global door_state, timer
    door_state = request.form.get("door_state", "unknown")
    timer = request.form.get("timer", 0.0)
    return "OK"