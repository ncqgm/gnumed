"""
Configuration model
This duplicates some of Karsten's work, but a configuration tool is required that talks to the
remote database
"""

import gmPG, gmExceptions, types, cPickle

#config = {}

# HACK FOR NOW
config = {'main.use_notebook':1, 'main.shadow':1, 'main.shadow.colour':(131, 129, 131), 'main.shadow.width':10}



def GetAllConfigs ():
    pool = gmPG.ConnectionPool ()
    conn = pool.GetConnection ('gmconfiguration')
    cur = conn.cursor ()
    cur.execute ("SELECT name, value, string FROM v_my_config")
    result = cur.fetchall ()
    pool.ReleaseConnection ('gmconfiguration')
    for row in result:
        if row[2] is None:
            config[row[0]] = row[1]
        else:
            config[row[0]] = row[2]

def SetConfig (key, value):
    pool = gmPG.ConnectionPool ()
    config[key] = value
    conn = pool.GetConnection ('gmconfiguration')
    cur = conn.cursor ()
    if type (value) == types.IntType:
        cur.execute ("UPDATE v_my_config SET value=%d WHERE name='%s'" % (value, key))
    elif type (value) == types.StringType:
        cur.execute ("UPDATE v_my_config SET string='%s' WHERE name='%s'" % (value, key))
    else:
        raise gmExceptions.ConfigError ('type not supported')
    pool.ReleaseConnection ('gmconfiguration')
    


