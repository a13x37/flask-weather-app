from datetime import datetime


def units_output(units):
    ''' Выбираем единицы измерения. '''
    if units == 'metric':
        return {'degrees': 'C\u00b0', 'wind': 'm/s', 'pressure': 'mmHg'}
    elif units == 'imperial':
        return {'degrees': 'F\u00b0', 'wind': 'mph', 'pressure': "inHg"}


def wind_arrow(direction):
    ''' Преобразуем направление ветра в стрелку для текстового вывода. '''
    if direction in range(23, 67):
        return '\u2b0b'
    elif direction in range(68, 112):
        return '\u2b05'
    elif direction in range(113, 157):
        return '\u2b09'
    elif direction in range(158, 202):
        return '\u2b06'
    elif direction in range(203, 247):
        return '\u2b08'
    elif direction in range(248, 292):
        return '\u2b95'
    elif direction in range(293, 337):
        return '\u2b0a'
    elif direction in range(338, 360):
        return '\u2b07'
    elif direction in range(0, 22):
        return '\u2b07'


def date_converter(timestamp):
    date = datetime.fromtimestamp(timestamp)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    day_of_week = days[date.weekday()]
    converted_date = date.strftime("%d.%m")
    return day_of_week, converted_date
