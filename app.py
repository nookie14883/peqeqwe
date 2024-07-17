from flask import Flask, send_from_directory, request, jsonify, Response
import os
from datetime import datetime
import logging
import requests
from dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

STATIC_FOLDER = 'static'
LOG_FOLDER = 'logs'
VK_API_URL = 'https://api.vk.com/method/wall.post'
VK_ACCESS_TOKEN = 'vk1.a.C_p1oysGXagbyb_W74POdMRYcMZTSqhxOKeW8jxKON9cQ6R0VtXzztw3RIV-MQsBJILBlJGXG4dJK99ZNon_kmQus80hBmuia2pJm465U6WXa_oD9VuY4oAt_Ewn15ERQpVmMDl3A1s7m4U0OaY0jl3Ucf0yfR0dACuGLJSJ2Qbp7ksDiLEJSB4HbO8TLZwzgX7PGkDBfreKvsE-v5jRBw'
VK_GROUP_ID = '226321035'
VK_API_VERSION = '5.131'

os.makedirs(LOG_FOLDER, exist_ok=True)

# Инициализация логирования
logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, 'app.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def send_vk_message(message):
    params = {
        'owner_id': f'-{VK_GROUP_ID}',  # Отрицательное значение для отправки в группу
        'message': message,
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_API_VERSION
    }
    response = requests.post(VK_API_URL, params=params)
    logging.debug(f"VK response: {response.json()}")
    return response.json()

def log_and_update_counter(ip, user_agent):
    timestamp = datetime.now()
    current_date = timestamp.strftime('%d-%m-%Y')
    message = (
        f"Timestamp: {timestamp}, IP: {ip}, User Agent: {user_agent}\n"
        f"Date: {current_date}, Counter updated"
    )
    logging.debug(f"Logging visit and updating counter: {message}")
    send_vk_message(message)

@app.route('/pixel.png')
def tracking_pixel():
    try:
        log_and_update_counter(request.remote_addr, request.headers.get('User-Agent'))
        return send_from_directory(STATIC_FOLDER, 'pixel.png')
    except Exception as e:
        app.logger.error(f"Error logging visit: {e}")
        logging.error(f"Exception occurred: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5003
    logging.info(f"Starting server at {host}:{port}")
    app.run(host=host, port=port, debug=True)
