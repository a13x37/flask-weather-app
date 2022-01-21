import requests
import os

from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'thisisasecret'

API_TOKEN = os.environ['API_TOKEN']

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_weather(
        city=None,
        units='metric'
        ):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': API_TOKEN,
        'units': units
        }
    api_data = requests.get(url, params).json()
    return api_data


@app.route('/')
def index_get():
    cities = City.query.all()
    print('cities=', cities)
    weather_data = []
    for city in cities:
        r = get_weather(city.name)
        print(r)
        pressure = r['main']['pressure']
        pressure *= 0.750062
        print(pressure)
        weather = {
            'city': city.name,
            'temperature': round(r['main']['temp'], 1),
            'description': r['weather'][0]['main'],
            'humidity': r['main']['humidity'],
            'wind_speed': r['wind']['speed'],
            'wind_dir': r['wind']['deg'],
            'sunrise': r['sys']['sunrise'],
            'sunset': r['sys']['sunset'],
            'timezone': r['timezone'],
            'icon': r['weather'][0]['icon'],
            'pressure': round(pressure)
        }
        weather_data.append(weather)

    return render_template('index.html', weather_data=reversed(weather_data))


@app.route('/', methods=['POST'])
def index_post():
    error_msg = ''
    new_city = request.form.get('city')

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            r = get_weather(new_city)
            if r['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_msg = ' City not found!'
        else:
            db.session.delete(existing_city)
            new_city_obj = City(name=new_city)
            db.session.add(new_city_obj)
            db.session.commit()
            error_msg = "City already exists!"
    if error_msg:
        flash(error_msg, 'error')

    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index_get'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
