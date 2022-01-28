import requests
import os
import uuid
import json
import datetime

from utils import wind_arrow, units_output, date_converter

from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID


app = Flask(__name__)
# app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
API_TOKEN = os.environ['API_TOKEN']


db = SQLAlchemy(app)
dt = datetime.datetime.now()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    cities = db.Column(db.String(500), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default=datetime.datetime.now(),
                           onupdate=datetime.datetime.now())
    city = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    platform = db.Column(db.String(50), nullable=True)
    browser = db.Column(db.String(50), nullable=True)
    browser_version = db.Column(db.String(50), nullable=True)


# values for index.html (radiobutton in menu)
units = "metric"
units_value = units_output(units)
units_metric_checked = "checked"
units_imperial_checked = None


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
        units='metric',
        coordinates=None
        ):
    url = "https://api.openweathermap.org/data/2.5/onecall"
    # if city:
    #     coordinates = get_coordinates(city)
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


# get user ip and city for first weather card
def get_start_city():
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        response = requests.get("https://ipinfo.io/{}/json".format(ip_address))
        data_json = response.json()
        location = data_json['loc'].split(',')
        lat = round(float(location[0]), 2)
        lon = round(float(location[1]), 2)
        city = data_json['city']
        country = data_json['country']
        user_agent = request.user_agent     # get browser info
        user_info = {
            'city': city,
            'country': country,
            'platform': user_agent.platform,
            'browser': user_agent.browser,
            'browser_version': user_agent.version
            }
        return [lat, lon, city, user_info]
    except Exception as e:
        print(e)
        return ['55.75', '37.61', 'Moscow']


# set session lifetime = 30 days
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(days=30)


@app.route('/')
def index_get():
    # check the user's open session.  If not, open it
    if 'uid' not in session:
        session['uid'] = uuid.uuid4()
    uid = session['uid']
    # looking for a user in the database by his UUID, get his list of cities
    user = Users.query.filter_by(uuid=uid).first()
    if user:
        user_cities = json.loads(user.cities)
        user.updated_on = datetime.datetime.now()
        db.session.commit()
    else:
        start = get_start_city()
        start_city = json.dumps([start[2], ])
        new_user = Users(uuid=uid,
                         cities=start_city,
                         city=start[3].get('city'),
                         country=start[3].get('country'),
                         platform=start[3].get('platform'),
                         browser=start[3].get('browser'),
                         browser_version=start[3].get('browser_version')
                         )
        user_cities = json.loads(new_user.cities)
        db.session.add(new_user)
        db.session.commit()

    weather_data = []
    # get the weather
    for city in user_cities:
        r = [get_weather(city, units), ]
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

    # check the position of the radio button (index.html -> menu)
    new_units = request.form.get('units_radio')
    if new_units:
        units = new_units
        units_value = units_output(units)
        units_metric_checked, units_imperial_checked = units_imperial_checked, units_metric_checked

    error_msg = ''
    # check the input of a new city
    new_city = request.form.get('city')
    if new_city:
        r = get_weather(new_city)
        if r:
            existing_city = r[0]['city']
            user = Users.query.filter_by(uuid=session['uid']).first()
            user_cities = json.loads(user.cities)
            if existing_city in user_cities:
                user_cities.remove(existing_city)
            user_cities.append(existing_city)
            user.cities = json.dumps(user_cities)
            user.updated_on = datetime.datetime.now()
            db.session.commit()
        else:
            error_msg = 'City not found!'
    if error_msg:
        flash(error_msg, 'error')

    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete_city(name):
    '''
    Remove city card.
    We get a list of users cities from the database,
    and then remove the city by NAME from the list and return the list to the database.
    '''
    user = Users.query.filter_by(uuid=session['uid']).first()
    user_cities = json.loads(user.cities)
    user_cities.remove(name)
    Users.query.filter_by(uuid=session['uid']).update({'cities': json.dumps(user_cities),
                                                       'updated_on': datetime.datetime.now()})
    db.session.commit()
    return redirect(url_for('index_get'))


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/getip')
def get_ip():
    ip_addr = request.remote_addr
    print('request.remote_addr', ip_addr)
    ip_addr = request.environ['REMOTE_ADDR']
    print('environ["REMOTE_ADDR"]', ip_addr)
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    print('get("HTTP_X_FORWARDED_FOR")', ip_addr)
    return redirect(url_for('index_get'))


# handling possible errors
@app.errorhandler(500)
def error_505_page(error):
    return render_template('error_page.html'), 500


@app.errorhandler(404)
def error_404_page(error):
    return render_template('error_page.html'), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
