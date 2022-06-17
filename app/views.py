import os
from datetime import datetime
import requests as requests
from flask import Blueprint, jsonify, request, abort
from app.auth.views import token_required

views = Blueprint('views', __name__)


def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={os.getenv('WEATHER_API_KEY')}"
    r = requests.get(url).json()
    if not r:
        abort(400)
    coord = {'lat': r[0]['lat'], 'lon': r[0]['lon']}
    return coord


def get_weather(coordinates):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={coordinates['lat']}&lon={coordinates['lon']}" \
          f"&units=metric&appid={os.getenv('WEATHER_API_KEY')}"
    r = requests.get(url).json()
    weather = {}
    weather['city'] = r['name']
    weather['weather'] = r['weather'][0]['main']
    weather['temp'] = round(r['main']['temp'])
    weather['sunrise'] = datetime.fromtimestamp(r['sys']['sunrise']).strftime('%H:%M')
    weather['sunset'] = datetime.fromtimestamp(r['sys']['sunset']).strftime('%H:%M')
    return weather


@views.route('/weather', methods=['POST'])
@token_required
def show_weather():
    data = request.json
    city = data.get('city')
    if city is None or len(city) == 0:
       return jsonify({"message": "Program can't get current GPS coordinates"})
    coordinates = get_coordinates(city)
    weather = get_weather(coordinates)
    return jsonify({'weather:': weather})

