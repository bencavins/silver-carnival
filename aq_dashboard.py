"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from openaq import OpenAQ


app = Flask(__name__) 
api = OpenAQ()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


class Record(DB.Model):
    # id (integer, primary key)
    id = DB.Column(DB.BigInteger, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"Record<{self.id}, {self.datetime}, {self.value}>"


def get_results():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    data_list = []
    for result in body['results']:
        my_tuple = (result['date']['utc'], result['value'])
        data_list.append(my_tuple)
    return data_list


@app.route('/')
def root():
    """Base view."""

    return str(get_results())


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    
    for datetime, value in get_results():
        record = Record(datetime=datetime, value=value)
        DB.session.add(record)

    DB.session.commit()
    return 'Data refreshed!'