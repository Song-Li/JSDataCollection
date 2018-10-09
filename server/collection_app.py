from flask import Flask, request,make_response, current_app
import os
import md5
from flask_failsafe import failsafe
import flask
from flask_cors import CORS, cross_origin
import json
import hashlib
from flaskext.mysql import MySQL
import ConfigParser
import re
import numpy as np
from PIL import Image
import base64
import cStringIO
from datetime import datetime
from urllib2 import urlopen
from django.utils.encoding import smart_str, smart_unicode

root = "/home/sol315/server/uniquemachine/"
pictures_path = "/home/sol315/pictures/"
config = ConfigParser.ConfigParser()
config.read(root + 'password.ignore')

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'username')
app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DATABASE_DB'] = 'uniquemachine'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
CORS(app)
base64_header = "data:image/png;base64,"

def run_sql(sql_str):
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute(sql_str)
    db.commit()
    res = cursor.fetchall() 
    return res

# update one feature requested from client to the database asynchronously.
# before this function, we have to make sure
# every feature is included in the sql server
def doUpdateFeatures(unique_label, data):
    update_str = ""
    for key, value in data.iteritems():
        update_str += '{}="{}",'.format(key, value)

    update_str = update_str[:-1]
    sql_str = 'UPDATE features SET {} WHERE uniquelabel = "{}"'.format(update_str, unique_label)
    res = run_sql(sql_str)
    genFingerprint(unique_label)
    return res 

def doInit(unique_label, cookie):

    result = {}
    agent = ""
    accept = ""
    encoding = ""
    language = ""
    IP = ""
    keys = ""
    try:
        agent = request.headers.get('User-Agent')
        accept = request.headers.get('Accept')
        encoding = request.headers.get('Accept-Encoding')
        language = request.headers.get('Accept-Language')
        keys = '_'.join(request.headers.keys())
        IP = request.remote_addr
    except:
        print keys
        pass

    # create a new record in features table
    sql_str = "INSERT INTO features (uniquelabel, IP) VALUES ('{}', '{}')".format(unique_label, IP)
    run_sql(sql_str)

    # update the statics
    result['agent'] = agent
    result['accept'] = accept
    result['encoding'] = encoding
    result['language'] = language
    result['label'] = cookie
    # remove iplocation
    result['httpheaders'] = keys 

    return doUpdateFeatures(unique_label, result)

@app.route("/getCookie", methods=['POST'])
def getCookie():
    IP = request.remote_addr
    id_str = IP + str(datetime.now()) 
    unique_label = hashlib.sha1(id_str).hexdigest()

    cookie = request.values['cookie']
    sql_str = 'SELECT count(id) FROM cookies WHERE cookie = "{}"'.format(cookie)
    res = run_sql(sql_str)

    if res[0][0] == 0:
        cookie = unique_label 
        sql_str = "INSERT INTO cookies (cookie) VALUES ('" + cookie + "')"
        run_sql(sql_str)

    doInit(unique_label, cookie)
    return unique_label + ',' + cookie

@app.route("/check_exist_picture", methods=['POST'])
def check_exsit_picture():
    hash_value = request.values['hash_value']
    sql_str = "SELECT count(dataurl) FROM pictures WHERE dataurl='" + hash_value + "'"
    res = run_sql(sql_str)

    if res[0][0] > 0: 
        return '1'
    else:
        return '0'

@app.route("/pictures", methods=['POST'])
def store_pictures():
    # get ID for this picture
    image_b64 = request.values['imageBase64']
    hash_value = hashlib.sha1(image_b64).hexdigest()

    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "INSERT INTO pictures (dataurl) VALUES ('" + hash_value + "')"
    cursor.execute(sql_str)
    db.commit()

    # remove the define part of image_b64
    image_b64 = re.sub('^data:image/.+;base64,', '', image_b64)
    # decode image_b64
    image_data = image_b64.decode('base64')
    image_data = cStringIO.StringIO(image_data)
    image_PIL = Image.open(image_data)
    image_PIL.save("/home/sol315/pictures/" + str(hash_value) + ".png")
    return hash_value 

@app.route('/updateFeatures', methods=['POST'])
def updateFeatures():
    result = request.get_json()
    unique_label = result['uniquelabel']
    features = {}

    for feature in result.iterkeys():
        value = result[feature]

        #fix the bug for N/A for cpu_cores
        if feature == 'cpu_cores':
            value = int(value)

        features[feature] = value

    doUpdateFeatures(unique_label, features)
    return flask.jsonify({'finished': features.keys()})
