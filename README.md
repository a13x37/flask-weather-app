# Weather App 
A simple weather app build with Flask. 
You can select cities and watch the weather for them.
City cards are protected from re-adding and can be deleted.
You can select the unit of measurement in the settings menu.

OpenWeatherMap API used to get weather data.
MDBootstrap used for design page.
SQLAlchemy is used to work with the database.

## Features
- Search/delete city `done`
- Units choice `done`
- 5 days forecast `done`
- geo ip detection `done`

## Setup
- `pip install -r requirements.txt`
- Add environment variables:
  - `API_TOKEN="###############"`. your OpenWeatherMap API token.
  - add `SECRET_KEY="********"`random string.
  - `DATABASE_URI` - you database URI
- Run
  - `python app.py`

## Usage

![Usage](https://github.com/a13x37/flask-weather-app/blob/master/static/usage.gif)

![Desktop](https://github.com/a13x37/flask-weather-app/blob/master/static/weather_desk.png)

![Mobile](https://github.com/a13x37/flask-weather-app/blob/master/static/weather_mobile.png)
