from flask import Flask, render_template, g, request, jsonify
import pandas as pd
import sqlite3
import xml.etree.ElementTree as ET
import urllib
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, Form
from wtforms.validators import DataRequired
import wtforms as wt
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/map')
def maps():
    return render_template('map.html')

@app.route('/map-hometown')
def map_hometown():
    return render_template('map-hometown.html')

@app.route('/networks')
def networks():
    return render_template('networks.html')

@app.route('/networks-education')
def networks_education():
    return render_template('networks-education.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


##PYTHONANYWHERE REQUIRES ABSOLUTE PATH: '/home/stewart/mysite/ag_scientist.db'
DATABASE = 'ag_scientist.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/CASDB', methods=['POST', 'GET'])
def CASDBOnline():
    form = MyForm()
    database = get_db()
    bioQuery = ""
    edQuery = ""
    emQuery = ""
    query = ""
    full = "TRUE"
    if request.method == 'POST':
        if request.form['btn'] == 'Search':
            name = request.form['name']
            gender = request.form['gender']
            prov = request.form['prov']
            institution = request.form['institution']
            #q = "SELECT DISTINCT * FROM scientists INNER JOIN education, institutions ON scientists.SCIENTIST_PK = education.SCIENTIST_FK AND education.INST_FK = institutions.INST_PK WHERE NAME LIKE '%" + name + "%' AND GENDER LIKE '%"+gender+"%' AND HT_PROV LIKE '%"+prov+"%' AND INST_NAME LIKE '%"+institution+"%';"
            q = "SELECT * FROM scientists WHERE NAME LIKE '%" + name + "%';"
            query = database.execute(q).fetchall()
            
            full = "TRUE"

        if request.form['btn'] == 'Clear':
            form.name.data = ""
            form.gender.data = ""
            form.prov.data = ""
            form.institution.data = ""
            q = "SELECT * FROM scientists"
            query = database.execute(q).fetchall()
            full="TRUE"

        if request.form['btn'] != 'Search' and request.form['btn'] != 'Clear':
            queryName = request.form['btn']
            bioQ = "SELECT * FROM scientists WHERE NAME = '"+ queryName + "';"
            bioQuery = database.execute(bioQ).fetchall()
            edQ = "SELECT * FROM education INNER JOIN scientists, institutions ON scientists.SCIENTIST_PK = education.SCIENTIST_FK AND education.INST_FK = institutions.INST_PK WHERE NAME = '"+ queryName + "';"
            edQuery = database.execute(edQ).fetchall()
            emQ = "SELECT * FROM employment INNER JOIN scientists ON scientists.SCIENTIST_PK = employment.SCIENTIST_FK WHERE scientists.NAME = '"+ queryName + "';"
            emQuery = database.execute(emQ).fetchall()
            full="FALSE"

    else:    
        q = "SELECT * FROM scientists"
        query = database.execute(q).fetchall()
        full="TRUE"

    return render_template('CASDB.html', queryData=query, bioQuery=bioQuery, edQuery=edQuery, emQuery=emQuery, form=form, full=full)


@app.route('/sample')
def sample():
    database = get_db()
    bioQ = "SELECT * FROM scientists WHERE NAME = '馮澤芳';"
    edQ = "SELECT * FROM education INNER JOIN scientists, institutions ON scientists.SCIENTIST_PK = education.SCIENTIST_FK AND education.INST_FK = institutions.INST_PK WHERE NAME = '馮澤芳';"
    bioQuery = database.execute(bioQ).fetchall()
    edQuery = database.execute(edQ).fetchall()
    return render_template('sample.html', bioQuery=bioQuery, edQuery=edQuery)

class MyForm(FlaskForm):
    name = StringField('姓名')
    gender = StringField('性別')
    prov = StringField('籍貫（省）')
    institution = StringField('機關')

@app.route('/autoName',methods=['GET'])
def autoName():
    search = request.args.get('autoName')
    db = get_db()
    q="SELECT NAME FROM scientists"
    result= db.execute(q).fetchall()
    NAMES= [i[0] for i in result]
    app.logger.debug(search)
    return jsonify(json_list=NAMES)

@app.route('/autoGender',methods=['GET'])
def autoGender():
    search = request.args.get('autoGender')
    db = get_db()
    q="SELECT GENDER FROM scientists"
    result= db.execute(q).fetchall()
    GENDER= list(set(filter(None, [i[0] for i in result])))
    app.logger.debug(search)
    return jsonify(json_list=GENDER)

@app.route('/autoProv',methods=['GET'])
def autoProv():
    search = request.args.get('autoProv')
    db = get_db()
    q="SELECT HT_PROV FROM scientists"
    result= db.execute(q).fetchall()
    PROV = list(set(filter(None, [i[0] for i in result])))
    app.logger.debug(search)
    return jsonify(json_list=PROV)

@app.route('/autoInst',methods=['GET'])
def autoInst():
    search = request.args.get('autoInst')
    db = get_db()
    q="SELECT INST_NAME FROM institutions"
    result= db.execute(q).fetchall()
    INST = list(set(filter(None,[i[0] for i in result])))
    app.logger.debug(search)
    return jsonify(json_list=INST)


@app.route('/api/coordinates') 
def coordinates():
    addresses = session.query(Coordinates)#however you query your db
    all_coods = [] # initialize a list to store your addresses
    for add in addresses:
        address_details = {
        "lat": add.lat, 
        "lng": add.lng, 
        "title": add.title}
        all_coods.append(address_details)
    return jsonify({'cordinates': all_coods})


if __name__ == "__main__":
    app.debug = True
    app.run()
