"""A small Flask API: GET /, GET /visits (a counter in Redis), GET /health."""
import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(message=os.environ.get("GREETING", "Hello from Python"), hostname=socket.gethostname())


@app.get("/visits")
def visits():
    import redis
    client = redis.Redis(host=os.environ.get("REDIS_HOST", "redis"), port=6379, socket_connect_timeout=2)
    return jsonify(visits=client.incr("visits"))


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
