#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weather Flask API app
Created on Sat Dec 22 22:56:46 2018
"""

# Import dependencies
from flask import Flask, jsonify

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc

from datetime import date
from datetime import timedelta
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


def daily_normals(date):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()

def duration_temperature(start_date,end_date):
    start_date_list = start_date.split('-')
    end_date_list = end_date.split('-')

    start_day_type = date(int(start_date_list[0]),int(start_date_list[1]),int(start_date_list[2]))
    end_day_type = date(int(end_date_list[0]),int(end_date_list[1]),int(end_date_list[2]))
    delta = end_day_type - start_day_type
    day_duration = delta.days

    start_day_type = date(int(start_date_list[0]),int(start_date_list[1]),int(start_date_list[2]))
    end_day_type = date(int(end_date_list[0]),int(end_date_list[1]),int(end_date_list[2]))
    delta = end_day_type - start_day_type
    day_duration = delta.days

    next_day_list =[]
    date_list =[]

    for i in range(day_duration+1):
        next_day_type = start_day_type + timedelta(days=i)
        day_str = next_day_type.strftime('%Y-%m-%d')
        next_day_list.append(day_str[5:])
        date_list.append(day_str)

    daily_normal_temp=[]
    for i in range(len(next_day_list)):
        daily_normal_temp.append(daily_normals(next_day_list[i])[0])
    
    # Build final dict list for jsonify
    dur_temp_list=[]
    for i in range(len(daily_normal_temp)):
        dur_temp_list.append({'date':date_list[i],\
                              'min temp':daily_normal_temp[i][0],\
                              'avg temp':daily_normal_temp[i][1],\
                              'max temp':daily_normal_temp[i][1]})
        
    return dur_temp_list

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Weather Analysis Apps API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"route example: /api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"route example: /api/v1.0/2017-01-01/2017-02-15<br/>"
    )

@app.route("/api/v1.0/precipitation")
def query_precipitation():

    date_prcp_query = session.query(Measurement.date,Measurement.prcp).all()
    date_prcp_list =[]
    for i in range(len(date_prcp_query)):
        date_prcp_list.append({'date':date_prcp_query[i][0],'precipitation':date_prcp_query[i][1]})
    
    return jsonify(date_prcp_list)


@app.route("/api/v1.0/stations")
def query_stations():
    
    station_query = session.query(Station.station,Station.name).all()
    station_list =[]
    for i in range(len(station_query)):
        station_list.append({'station':station_query[i][0],'name':station_query[i][1]})
    
    return jsonify(station_list)

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

@app.route("/api/v1.0/<start>")
# route example: /api/v1.0/2017-01-01

def query_date_start(start):
    
    #last_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    
    start_list = duration_temperature(start,'2017-08-23')
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
# route example: /api/v1.0/2017-01-01/2017-02-15
def query_date_start_end(start,end):
    
    start_end_list = duration_temperature(start,end)
    return jsonify(start_end_list)
        
if __name__ == "__main__":
    app.run(debug=True)
