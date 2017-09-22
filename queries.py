
# coding: utf-8

# In[1]:

import audit
import Data
import sqlite3
import csv
import pandas as pd


# In[2]:

con = sqlite3.connect("data.db")
con.text_factory = str
cur = con.cursor()

# create nodes table
cur.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")
with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['lat'], i['lon'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp'])              for i in dr]

cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp)                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con.commit()

#create nodes_tags table
cur.execute("CREATE TABLE nodes_tags (id, key, value, type);")
with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['key'], i['value'], i['type']) for i in dr]

cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
con.commit()

#Create ways table
cur.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")
with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]

cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
con.commit()

#Create ways_nodes table
cur.execute("CREATE TABLE ways_nodes (id, node_id, position);")
with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['node_id'], i['position']) for i in dr]

cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", to_db)
con.commit()

#Create ways_tags table
cur.execute("CREATE TABLE ways_tags (id, key, value, type);")
with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['key'], i['value'], i['type']) for i in dr]

cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
con.commit()


# In[4]:

con = sqlite3.connect("data.db")
cur = con.cursor()

def number_of_nodes():
    result = cur.execute('SELECT COUNT(*) FROM nodes')
    return result.fetchone()[0]
print "Number of nodes: " , number_of_nodes()


# In[5]:

def number_of_ways():
    result = cur.execute('SELECT COUNT(*) FROM ways')
    return result.fetchone()[0]
print "Number of ways: " , number_of_ways()


# In[6]:

def number_of_unique_users():
    result = cur.execute('SELECT COUNT(DISTINCT(e.uid))             FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e')
    return result.fetchone()[0]
print "Number of unique users: " , number_of_unique_users()


# In[7]:

def top_contributing_users():
    users = []
    for row in cur.execute('SELECT e.user, COUNT(*) as num             FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e             GROUP BY e.user             ORDER BY num DESC             LIMIT 10'):
        users.append(row)
    return users
print "Top contributing users:\n" , pd.DataFrame(top_contributing_users())


# In[8]:

def contributing_once():
    result = cur.execute('SELECT COUNT(*)         FROM        (SELECT e.user, COUNT(*) as num         FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e         GROUP BY e.user         HAVING num=1)')
    return result.fetchone()[0]
print contributing_once()


# In[15]:

def common_amenities():
    amenitites = []
    for row in cur.execute('SELECT value, COUNT(*) as num             FROM nodes_tags              WHERE key="amenity"             GROUP BY value             ORDER BY num DESC             LIMIT 10'):
        amenitites.append(row)
    return amenitites

print "Common ammenities:\n" , pd.DataFrame(common_amenities())


# In[16]:

def biggest_religion():
    for row in cur.execute('SELECT nodes_tags.value, COUNT(*) as num             FROM nodes_tags                 JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="place_of_worship") i                 ON nodes_tags.id=i.id             WHERE nodes_tags.key="religion"             GROUP BY nodes_tags.value             ORDER BY num DESC             LIMIT 1;'):
        return row
print "Biggest religion: " , biggest_religion()


# In[17]:

def popular_cuisine():
    cuisine=[]
    for row in cur.execute('SELECT nodes_tags.value, COUNT(*) as num             FROM nodes_tags                 JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="restaurant") i                 ON nodes_tags.id=i.id             WHERE nodes_tags.key="cuisine"             GROUP BY nodes_tags.value             ORDER BY num DESC             LIMIT 1'):
        cuisine.append(row)
    return cuisine
print "Popular cuisine: " , popular_cuisine()


# In[ ]:



