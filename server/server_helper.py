import user_agents

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

def get_browser_from_agent(agent):
    """
    return the browser type by the input agent
    """
    try:
        return ignore_non_ascii(user_agents.parse(agent).browser.family)
    except:
        return "agent error"

def get_browser_version(agent):
    """
    return the string of browser and version number
    if it's others, just return other
    """
    parsed = user_agents.parse(agent)
    return ignore_non_ascii(parsed.browser.family) + '#%' + ignore_non_ascii(parsed.browser.version_string)

def get_os_version(agent):
    """
    return the string of os and version number
    """
    parsed = user_agents.parse(agent)
    return ignore_non_ascii(parsed.os.family) + '#%' + ignore_non_ascii(parsed.os.version_string)

def get_os_from_agent(agent):
    try:
        parsed = user_agents.parse(agent)
        return ignore_non_ascii(parsed.os.family)
    except:
        return "os error"

def get_full_device(row):
    """
    get the full device infor including device family and brand
    """
    parsed = user_agents.parse(row['agent'])
    device = ignore_non_ascii(parsed.device.family)
    return '{} {}'.format(device, ignore_non_ascii(parsed.device.brand))

