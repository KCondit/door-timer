from flask import Flask, render_template, request, abort, jsonify
import os

app = Flask(__name__)

# Simple in-memory store
door_state = "unknown"
timer = 0.0
API_KEY = os.environ.get("DOOR_API_KEY", "changeme")

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        door_state=door_state,
        timer=int(float(timer))
    )

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
