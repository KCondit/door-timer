from flask import Flask, request, render_template_string, abort, jsonify
import os

app = Flask(__name__)

door_state = "unknown"
timer = 0.0
API_KEY = os.environ.get("DOOR_API_KEY", "changeme")

@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
        <h1>Door Timer</h1>
        <p>Door state: <b id="door-state">{{ door_state }}</b></p>
        <p>Timer: <b id="timer">{{ timer }} seconds</b></p>
        <script>
          function poll() {
            fetch('/status').then(r => r.json()).then(data => {
              document.getElementById('door-state').textContent = data.door_state;
              document.getElementById('timer').textContent = data.timer + ' seconds';
            });
          }
          setInterval(poll, 1000); // Poll every 1 second
        </script>
    """, door_state=door_state, timer=int(timer))

@app.route("/update", methods=["POST"])
def update():
    if request.form.get("api_key") != API_KEY:
        abort(403)
    global door_state, timer
    door_state = request.form.get("door_state", "unknown")
    try:
        timer = float(request.form.get("timer", 0.0))
    except ValueError:
        timer = 0.0
    return "OK"

@app.route("/status", methods=["GET"])
def status():
    return jsonify(door_state=door_state, timer=int(float(timer)))
