from server_helper import *
import os
import md5
from flask_failsafe import failsafe
import flask
import json
import hashlib
import re
from PIL import Image
import cStringIO
from datetime import datetime
from urllib2 import urlopen
import random

# update one feature requested from client to the database asynchronously.
# before this function, we have to make sure
# every feature is included in the sql server

'''
TODO: current this file can not be used because of the SQL injection
need to be updated somehow
'''


def doInit(unique_label):
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
    
    result['browser'], result['browserversion'], result['device'], result['os'],result['osversion'] = extractInfoFromAgent(agent)


    return doUpdateFeatures(unique_label, result)

@app.route("/getUniqueLabel", methods=['POST'])
def getUniqueLabel():
    IP = request.remote_addr
    id_str = IP + str(datetime.now()) + str(random.randint(1, 10000000))
    unique_label = hashlib.sha1(id_str).hexdigest()
    doInit(unique_label)
    return unique_label

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
