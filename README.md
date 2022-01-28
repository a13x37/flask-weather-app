# Weather App 

A simple weather app build with Flask.  
The first city card for new users is shown by their location.  
You can select cities and watch the weather for them.  
City cards are protected from re-adding also cards can be deleted.  
You can select the unit of measurement in the settings menu.  

OpenWeatherMap API used to get weather data.  
SQLAlchemy is used to work with the database (PostgreSQL).  
Python Flask app with Gunicorn WSGI server deployed on Heroku using Docker.  
MDBootstrap used for design page.  

## Features
- Search/delete city `done`
- Units choice `done`
- 5 days forecast `done`
- geo ip detection `done`

## Setup
- Add environment variables:
  - `API_TOKEN="###############"`. your OpenWeatherMap API token.
  - add `SECRET_KEY="**********"`random seret string.
  - `DATABASE_URI` - you database URI

## Usage

![Usage](https://github.com/a13x37/flask-weather-app/blob/master/static/usage.gif)

![Desktop](https://github.com/a13x37/flask-weather-app/blob/master/static/weather_desk.png)

![Mobile](https://github.com/a13x37/flask-weather-app/blob/master/static/weather_mobile.png)
