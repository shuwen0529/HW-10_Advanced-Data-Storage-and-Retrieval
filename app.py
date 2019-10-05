# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy import desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#reflect the db into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save a reference to the measurenment table as 'Measurement'
Measurement = Base.classes.measurement
# Save a reference to the station table as 'Station'
Station = Base.classes.station

#create a session
session = Session(engine)

#make an app instance
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Weather Analysis Apps API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"Provide the start date only; calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date<br/>"
        f"route example: /api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Provide the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.<br/>"
        f"route example: /api/v1.0/2017-01-01/2017-02-15<br/>"
    )

############
@app.route("/api/v1.0/precipitation")
def query_precipitation():

    date_prcp_query = session.query(Measurement.date,Measurement.prcp).all()
    date_prcp_list =[]
    for i in range(len(date_prcp_query)):
        date_prcp_list.append({'date':date_prcp_query[i][0],'precipitation':date_prcp_query[i][1]})
    
    return jsonify(date_prcp_list)

############
@app.route("/api/v1.0/stations")
def query_stations():
   
    station_query = session.query(Station.station,Station.name).all()
    station_list =[]
    for i in range(len(station_query)):
        station_list.append({'station':station_query[i][0],'name':station_query[i][1]})
    
    return jsonify(station_list)

############
@app.route("/api/v1.0/tobs")
def query_tobs():
    
    last_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    result = [str(datestr) for datestr in last_date]
    last_date_split = result[0].split('-')
    last_12_month_date = dt.date(int(last_date_split[0]),int(last_date_split[1]),int(last_date_split[2])) - dt.timedelta(365)
    
    last_12_month_date = dt.date(int(last_date_split[0]),int(last_date_split[1]),int(last_date_split[2])) - dt.timedelta(365)

    tobs_lastyear_query = session.query(Measurement.date,Station.station,Measurement.tobs).\
                        filter(func.datetime(Measurement.date) >= last_12_month_date).\
                        order_by(Measurement.date).\
                        all()
    tobs_lastyear_list =[]
    for i in range(len(tobs_lastyear_query)):
        tobs_lastyear_list.append({'date':tobs_lastyear_query[i][0],'station':tobs_lastyear_query[i][1],'temperature':tobs_lastyear_query[i][2]})

    return jsonify(tobs_lastyear_list)

############
@app.route("/api/v1.0/<start>") 
def start_range(start):

    start_date = session.query(Measurement.date,func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)) \
             .filter(Measurement.date >= start) \
             .group_by(Measurement.date).all()

    return jsonify(start_date)

############
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    range = session.query(Measurement.date,func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)) \
             .filter(Measurement.date >= start).filter(Measurement.date <= end) \
             .group_by(Measurement.date).all()

    return jsonify(range)

############
#run the app
if __name__ == '__main__':
    app.run(debug=True)