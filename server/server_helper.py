import user_agents
from flask_cors import CORS, cross_origin
import ConfigParser
import base64
from flaskext.mysql import MySQL
from flask import Flask, request,make_response, current_app

root = "/home/sol315/server/collector/"
pictures_path = "/home/sol315/pictures/"
config = ConfigParser.ConfigParser()
config.read(root + 'password.ignore')
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'username')
app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DATABASE_DB'] = 'collector'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
CORS(app)
base64_header = "data:image/png;base64,"

def ignore_non_ascii(str1):
    """
    this function will ignore the non ascii and non latin-1 chars
    """
    if not str1:
        return 'None'
    str1 = str1.encode('latin-1', errors = 'ignore').decode('latin-1')
    str1 = str1.encode('ascii', errors = 'ignore').decode('ascii')
    return str1

def doUpdateFeatures(unique_label, data):
    """
    take in the unique label and the data, update the database
    """
    update_str = ""
    for key, value in data.iteritems():
        update_str += '{}="{}",'.format(key, value)
    # remove the last , added to the string
    update_str = update_str[:-1]
    sql_str = 'UPDATE features SET {} WHERE uniquelabel = "{}"'.format(update_str, unique_label)
    res = run_sql(sql_str)
    return res 

def run_sql(sql_str):
    """
    execute a sql string and return the result
    """
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute(sql_str)
    db.commit()
    res = cursor.fetchall() 
    return res

def extractInfoFromAgent(agent):
    """
    return browser_type, browser_version, device_type, os_type, os_version
    """
    parsed = user_agents.parse(agent)
    browser_type = ignore_non_ascii(parsed.browser.family)
    browser_version = ignore_non_ascii(parsed.browser.version_string)
    device_type = '{}_{}'.format(ignore_non_ascii(parsed.device.family), ignore_non_ascii(parsed.device.brand))
    os_type = ignore_non_ascii(parsed.os.family)
    os_version = ignore_non_ascii(parsed.os.version_string)
    return browser_type, browser_version, device_type, os_type, os_version

