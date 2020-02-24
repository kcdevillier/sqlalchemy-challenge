import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, render_template
import datetime as dt
from collections import defaultdict 


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def index():
        #Render Html which contains list of api's
        return render_template('index.html') 

@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session from Python to DB
    session = Session(engine)

    #query station, date & prcp
    date_prcp = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #convert list of tuples into normal list
    pres = defaultdict(list) 
    for i, row in date_prcp: 
        pres[i].append(row) 

    return jsonify(pres)

@app.route("/api/v1.0/stations")
def stations():
    #create session from Python to DB
    session = Session(engine)

    #query Distinct station names
    stations = session.query(Station.name.distinct()).all()
    session.close()
    #convert list of tuples into normal list
    names = list(np.ravel(stations))

    return jsonify(names)
    
@app.route("/api/v1.0/tobs")
def tobs():
    #create session from Python to DB
    session = Session(engine)
    
    #set date query parameter to 12 months prior to last date entry
    query_date = dt.date(2017, 8, 23) - dt.timedelta(weeks=52)

    #query dates and temperature observations from a year from the last data point.
    sel = ['Measurement.station', 'Measurement.date', 'Measurement.tobs']
    last_year_temps = session.query(*sel).filter(Measurement.date > query_date).all()
    session.close()
    
    #convert list of tuples into normal list
    last_temps = list(np.ravel(last_year_temps))

    return jsonify(last_temps)

@app.route("/api/v1.0/<start>/<end>")
def start(start, end):
    
    session = Session(engine)
    
    sel = [Station.name,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]

    if end == '9999':
        results_q = session.query(*sel).filter(Measurement.date >= start).group_by(Station.name).filter(Measurement.station==Station.station).all()
    
    else:
        results_q = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Station.name).filter(Measurement.station==Station.station).all()

    
    #convert query into dictionary
    results_d = {sub[0]: sub[1:] for sub in results_q}
    session.close()

    return jsonify(results_d)

# @app.route("/api/v1.0/<start>/<end>")
# def start(start, end):
    
#     session = Session(engine)
    
#     sel = [Station.name,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]
#     
    
#     #convert query into dictionary
#     results_d = {sub[0]: sub[1:] for sub in results_q}
#     session.close()

#     return jsonify(results_d)

if __name__ == '__main__':
    app.run(debug=True)
