import requests
import os

from utils import wind_arrow, units_output, date_converter

from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
API_TOKEN = os.environ['API_TOKEN']




db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


units = "metric"
units_value = units_output(units)


def get_coordinates(city):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': city,
        'appid': API_TOKEN,
        'limit': '1'
        }
    api_data = requests.get(url, params).json()
    if api_data:
        coordinates = {
            'city_name': api_data[0]['name'],
            'lat': api_data[0]['lat'],
            'lon': api_data[0]['lon']
            }
    else:
        coordinates = False
    return coordinates


def get_weather_values(data, city=None):
    pressure = data['pressure']
    pressure *= 0.750062
    weather_values = {
        'date': date_converter(data['dt'])[1],
        'day_of_week': date_converter(data['dt'])[0],
        'sunrise': data['sunrise'],
        'sunset': data['sunset'],
        'humidity': data['humidity'],
        'pressure': round(pressure),
        'wind_speed': round(data['wind_speed'], 1),
        'wind_dir': wind_arrow(data['wind_deg']),
        'description': data['weather'][0]['main'],
        'icon': data['weather'][0]['icon'],
        'wind_unit': units_output(units)['wind'],
        'pressure_unit': units_output(units)['pressure'],
        'temp_unit': units_output(units)['degrees'],
        'city': city
        }
    if isinstance(data['temp'], float) or isinstance(data['temp'], int):
        upd = {
            'temp': round(data['temp'], 1)
            }
    else:
        upd = {
            'temp_day': round(data['temp']['day']),
            'temp_night': round(data['temp']['night'])
            }
    weather_values.update(upd)
    return weather_values


def get_weather(
        city=None,
        units='metric'
        ):
    url = "https://api.openweathermap.org/data/2.5/onecall"
    coordinates = get_coordinates(city)
    weather_data = []
    if coordinates:
        params = {
            'lat': round(coordinates['lat'], 2),
            'lon': round(coordinates['lon'], 2),
            'appid': API_TOKEN,
            'units': units,
            'exclude': 'minutely,alerts,hourly'
            }
        api_data = requests.get(url, params).json()

        weather_data.append(get_weather_values(
                                    api_data['current'],
                                    coordinates['city_name'])
                            )

        for day in api_data['daily']:
            values = get_weather_values(day)
            weather_data.append(values)
    return weather_data


units_metric_checked = "checked"
units_imperial_checked = None


@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []
    for city in cities:
        r = [get_weather(city.name, units), ]

        weather_data.append(r)
    return render_template('index.html',
                           weather_data=reversed(weather_data),
                           checked1=units_metric_checked,
                           checked2=units_imperial_checked
                           )


@app.route('/', methods=['POST'])
def index_post():
    global units
    global units_value
    global units_metric_checked
    global units_imperial_checked
    new_units = request.form.get('units_radio')
    if new_units:
        units = new_units
        units_value = units_output(units)
        units_metric_checked, units_imperial_checked = units_imperial_checked, units_metric_checked

    error_msg = ''
    new_city = request.form.get('city')

    if new_city:
        r = get_weather(new_city)
        if r:
            existing_city = City.query.filter_by(name=r[0]['city']).first()
            if existing_city:
                db.session.delete(existing_city)

            new_city_obj = City(name=r[0]['city'])
            db.session.add(new_city_obj)
            db.session.commit()
            # error_msg = "City already exists!"
        else:
            error_msg = ' City not found!'
    if error_msg:
        flash(error_msg, 'error')

    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index_get'))


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.errorhandler(500)
def error_505_page(error):
    return render_template('error_page.html'), 500


@app.errorhandler(404)
def error_404_page(error):
    return render_template('error_page.html'), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
