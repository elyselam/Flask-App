import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import inspect, create_engine, func

from flask import Flask, render_template, jsonify

# Database Setup
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# Reflecting existing database into new model
Base = automap_base()
# Reflicting the tables
Base.prepare(engine, reflect=True)

# Save reference to each table in database (3)
Otu = Base.classes.otu
Samples = Base.classes.samples
Samples_metadata = Base.classes.samples_metadata

# Create link from Python to database
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def index():
    # testing query of database and rendering result
    # this page will eventually return dashboard homepage
    getback = session.query(Samples_metadata.ETHNICITY).all()
    response = list(np.ravel(getback))

    # below will be the plotly plots
    

    return render_template('index.html', test=response)

@app.route("/names")
def names():
    namedata = session.query(Samples_metadata.SAMPLEID).all()
    namelist = list(np.ravel(namedata))
    clean_namelist = []
    for element in namelist:
        clean_namelist.append("BB_" + str(element))
    return jsonify(clean_namelist)

@app.route("/otu")
def otus():
    otudata = session.query(Otu.lowest_taxonomic_unit_found).all()
    otulist = list(np.ravel(otudata))
    return jsonify(otulist)

@app.route("/otu_search/<idlist_string>")
def otu_by_id(idlist_string):
    idlist = idlist_string.replace('[', '').replace(']', '').replace("'", "").split(',')
    
    output = []
    
    for i in idlist:
        otudata = session.query(Otu).filter_by(otu_id=int(i)).first()
        match = otudata.lowest_taxonomic_unit_found
        output.append(match)
    return jsonify(output)

@app.route("/metadata/<sample>")
def metadata(sample):
    input_sample = int(sample.replace('BB_', ''))
    sampledata = session.query(Samples_metadata).filter_by(SAMPLEID=input_sample).first()
    return jsonify({"AGE": sampledata.AGE,
                    "BBTYPE": sampledata.BBTYPE,
                    "ETHNICITY": sampledata.ETHNICITY,
                    "GENDER": sampledata.GENDER,
                    "LOCATION": sampledata.LOCATION,
                    "SAMPLEID": sampledata.SAMPLEID
                    })

@app.route("/wfreq/<sample>")
def wfreq(sample):
    input_sample = int(sample.replace('BB_', ''))
    sampledata = session.query(Samples_metadata).filter_by(SAMPLEID=input_sample).first()
    return jsonify(sampledata.WFREQ)

@app.route("/samples/<sample>")
def samples(sample):
    input_sample = str(sample)
    sampledata = session.query(Samples).order_by(getattr(Samples, input_sample).desc())
    otu_list = []
    value_list = []
    for element in sampledata:
        otu_list.append(str(np.ravel(element.otu_id)[0]))
        value_list.append(str(np.ravel(getattr(element, input_sample))[0]))
    return jsonify([{
        "otu_ids": otu_list,
        "sample_values": value_list
    }])

if __name__ == '__main__':
    app.run(debug=True)