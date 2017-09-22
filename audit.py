
# coding: utf-8

# In[4]:

import csv
import codecs
import xml.etree.cElementTree as ET 
from collections import defaultdict
import re
import pprint
import os

OSM_FILE = "location.osm" 


# In[2]:

#Code for generating sample
SAMPLE_FILE = "sample.osm"

k = 10 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# In[5]:

#Tag names with count
tags={}
def count_tags(filename):
    for event,elem in ET.iterparse(filename):
        if elem.tag in tags.keys():
            tags[elem.tag]+=1
        else:
            tags[elem.tag] = 1
    return tags
                
pprint.pprint(count_tags(OSM_FILE))


# In[6]:

#check the "k" value for each "<tag>" and see if there are any potential problems
#"lower", for tags that contain only lowercase letters and are valid,
#"lower_colon", for otherwise valid tags with a colon in their names,
#"problemchars", for tags with problematic characters, and
#"other", for other tags that do not fall into the other three categories.

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys['lower'] += 1              
        elif lower_colon.search(element.attrib['k']):           
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
            
        pass
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

pprint.pprint(process_map(OSM_FILE))


# In[7]:

#Finding different street types with count

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE) #gets any no. of non-white space characters and '.' at end of the string
street_types = defaultdict(int)

def audit_street_type(street_types, street_name): #Search for words which match the re, group and count the street types
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1 #incrementing the value associated with a particular street_type(which is the key)
        
def print_sorted_dict(d): 
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower()) #for printing in alphabetical order regardless of case
    for k in keys:
        v = d[k] #v equals value corresponding to each key
        print ("%s: %d" % (k, v)) #printing key: value pairs

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(OSM_FILE):
        if is_street_name(elem):
            audit_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types) 
    

if __name__ == '__main__':
    audit()


# In[11]:

#Updating street names based on expected list and mapping
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Lane", "Road", "Nagar", "Extension", "T.Nagar", "Pathai", "Quarters"]

mapping = { "St": "Street",
            "St.": "Street",
            "STREET": "Street",
            "STREETS": "Street",
            "street": "Street",
            "strret": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Rd": "Road",
            "road": "Road",
            "Extn.": "Extension",
            "pathai": "Pathai",
            "quarters": "Quarters", 
            }


def audit_street_type(street_types, street_name): 
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

    
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m is not None:
        if m.group() not in expected:
            if m.group() in mapping.keys():
                #replacing street names in 'name' with those in mapping
                name = re.sub(m.group(), mapping[m.group()], name)
            elif name.find(','):        
                position=name.find(',')
                if position >0:           #If comma is present, position value is greater than 0
                    name=name[:position]  #Words before the comma are taken as street names
                    if name.isdigit(): #Street names are not represented by digits only
                        name=''                        
            else:
                name=name
    return name


def test():
    st_types = audit(OSM_FILE)

    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            #print(better_name)
            print (name, "=>", better_name)


if __name__ == '__main__':
    test()


# In[13]:

#Auditing phone numbers
#White space between the numbers have been removed 
#To have uniformity in the data format the country code and STD code have been removed
#Phone numbers of invalid number of digits have been removed

def audit_phone_type(phone_types,phone_name):
    phone_types.add(phone_name)
        
def is_phone_number(elem):
    return (elem.attrib['k'] == 'phone')

def audit_phone(osmfile):
    osm_file = open(osmfile, "r")
    phone_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_number(tag):
                    audit_phone_type(phone_types, tag.attrib['v'])
    return phone_types

def update_phones(phonenumber):
    # remove non-digit characters
    phonenumber = ''.join(ele for ele in phonenumber if ele.isdigit())
    
    if phonenumber.startswith('91'): #country code of India is 91
        phonenumber  = phonenumber[2:]
    if phonenumber.startswith('044'): #STD code for chennai is 044
        phonenumber  = phonenumber[3:]
    if phonenumber.startswith('044 '): 
        phonenumber  = phonenumber[4:]

    #In India, landline phone numbers have 8 digits and mobile phone numbers have 10 digits. 
    #Remove numbers of other lengths      
    #Exception: toll-free numbers may start with 1800 and have 11 characters
    if len(phonenumber)==10 or len(phonenumber)==8 :
        phonenumber=phonenumber
    else:
        if phonenumber.startswith('1800') and len(phonenumber)==11:
            phonenumber=phonenumber 
        else:
            phonenumber = ''            
    return phonenumber


ph_list = audit_phone(OSM_FILE)

# printing the original numbers and updated numbers
for phone_number in ph_list:
    print phone_number, '==>',
    phone_number = update_phones(phone_number)
    print phone_number

