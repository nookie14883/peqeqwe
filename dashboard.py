from flask import Blueprint, jsonify, Response, request
import logging
import requests
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)
VK_API_URL = 'https://api.vk.com/method/wall.get'
VK_ACCESS_TOKEN = 'vk1.a.C_p1oysGXagbyb_W74POdMRYcMZTSqhxOKeW8jxKON9cQ6R0VtXzztw3RIV-MQsBJILBlJGXG4dJK99ZNon_kmQus80hBmuia2pJm465U6WXa_oD9VuY4oAt_Ewn15ERQpVmMDl3A1s7m4U0OaY0jl3Ucf0yfR0dACuGLJSJ2Qbp7ksDiLEJSB4HbO8TLZwzgX7PGkDBfreKvsE-v5jRBw'
VK_GROUP_ID = '226321035'
VK_API_VERSION = '5.131'

def check_auth(username, password):
    return username == 'lime_checker' and password == 'ldw12fggAgfgh3gG[[vRF'

# Запрос логина и пароля
def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

# Декоратор для защиты маршрута
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def get_wall_posts(count=1000):
    posts = []
    offset = 0
    while True:
        params = {
            'owner_id': f'-{VK_GROUP_ID}',
            'access_token': VK_ACCESS_TOKEN,
            'v': VK_API_VERSION,
            'count': 100,
            'offset': offset
        }
        response = requests.get(VK_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                items = data['response']['items']
                posts.extend(items)
                if len(items) < 100 or len(posts) >= count:
                    break
                offset += 100
            else:
                logging.error("Unexpected response format")
                break
        else:
            logging.error(f"Error fetching wall posts: {response.status_code}")
            break
    return posts

@dashboard_bp.route('/dashboard')
@requires_auth
def dashboard():
    try:
        posts = get_wall_posts()
        if not posts:
            return jsonify({"error": "Error retrieving wall posts"}), 500

        data = {}

        for post in posts:
            text = post['text']
            if "Counter updated" in text:
                date_line = text.split("\n")[1]
                date = date_line.split(": ")[1]
                if date in data:
                    data[date] += 1
                else:
                    data[date] = 1

        return jsonify(data)
    except Exception as e:
        logging.error(f"Error retrieving dashboard data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
