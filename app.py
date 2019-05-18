import numpy as np;
import datetime as dt;
import sqlalchemy;
from sqlalchemy.ext.automap import automap_base;
from sqlalchemy.orm import Session;
from sqlalchemy import create_engine, func;
import pandas as pd;
from pandas import DataFrame;

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

#reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine,reflect=True)

#Save reference to the table
Station = Base.classes.station

Measurement = Base.classes.measurement

#Create session(link) from Python to the DB
session = Session(engine)


#flask setup
app = Flask(__name__)


#Home page.
#List all routes that are available.
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


#/api/v1.0/precipitation
#Convert the query results to a Dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():

    #### I used ('2017-08-23') because it contains within the database
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    rainfall = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

    return jsonify(dict(rainfall))

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

#/api/v1.0/tobs
#query for the dates and temperature observations from a year from the last data point.
#Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():

    #### I used ('2017-08-23') that it contains within the database
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    temp = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()
 
    #dict provides list one by one -  easy to view for observation
    return jsonify(dict(temp))


#/api/v1.0/<start> 
##When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and
#  equal to the start date.

@app.route("/api/v1.0/<start>")
def start(start):

    start_date  = dt.datetime.strptime(start,'%Y-%m-%d')
    
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#/api/v1.0/<start>/<end>

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
# for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):

    start_date  = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date  = dt.datetime.strptime(end,'%Y-%m-%d')

    
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
        func.max(Measurement.tobs)).filter(Measurement.date >= start_date). \
        filter(Measurement.date <= end_date).group_by(Measurement.date).all()
         
         
    trip = list(trip_data)
    return jsonify(trip)
    
    
if __name__ == "__main__":
    app.run(debug=True)
