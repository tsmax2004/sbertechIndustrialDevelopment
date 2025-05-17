from flask import Flask, request, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler
import socket
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Prometheus metrics
log_requests_total = Counter('log_requests_total', 'Total number of /log requests')
log_requests_success = Counter('log_requests_success', 'Number of successful /log requests')
log_requests_failed = Counter('log_requests_failed', 'Number of failed /log requests')
request_duration = Histogram('request_duration_seconds', 'Request duration in seconds')

# Ensure logs directory exists
os.makedirs('/app/logs', exist_ok=True)

# Configure logging
handler = RotatingFileHandler('/app/logs/app.log', maxBytes=10000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route('/')
def hello():
    return f"Hello! (Pod: {socket.gethostname()})"

@app.route('/status')
def status():
    return jsonify({
        "status": "ok",
        "pod": socket.gethostname()
    })

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/log', methods=['POST'])
def log_message():
    log_requests_total.inc()
    with request_duration.time():
        data = request.get_json()
        if not data or 'message' not in data:
            log_requests_failed.inc()
            return jsonify({"error": "No message provided"}), 400
        
        app.logger.info(f"[Pod: {socket.gethostname()}] {data['message']}")
        log_requests_success.inc()
        return jsonify({
            "status": "ok",
            "pod": socket.gethostname()
        }), 200

@app.route('/logs')
def get_logs():
    try:
        with open('/app/logs/app.log', 'r') as f:
            logs = f.read()
        return logs
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
