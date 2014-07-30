"""
    survey_upload.py -- Read REDCap survey data and create add and sub rdf
    for addition to VIVO

    Version 0.1 MC 2014-07-28
    --  Initial version.

    To Do:
    write all the stubs -- the ustpo one is _difficult_
    
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2013, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivotools import read_csv
from datetime import datetime
from vivotools import get_vivo_value
from vivotools import get_vivo_uri
from vivotools import update_data_property
from vivotools import assert_resource_property
from vivotools import rdf_header
from vivotools import rdf_footer
from vivotools import vivo_sparql_query

import sys
import json
import codecs
import os

# Helper functions

def make_datetime(y, m, d):
    """
    Given three string which should have a year, month and a day,
    create integr values and return a datetime. Handle empty strings
    and None.
    """
    if y == '' or y is None:
        return None
    yn = int(y)
    if m == '' or m is None:
        mn = 1
    else:
        mn = int(m)
    if d == '' or d is None:
        dn = 1
    else:
        dn = int(d)
    try:
        dt = datetime(yn, mn, dn)
    except:
        dt = None
    return dt

def find_entity_uri(entity_type, entity_predicate, entity_value, debug=False):
    """
    Given a type and a predicate and its value, find the uri of the first
    entity of that type, with that predicate.

    Example:

    find_entity_uri('skos:Concept', 'rdfs:label', 'Pulmonary Hypertension')

    if not found, return None
    """
    query = """
        SELECT ?uri
        WHERE {
            ?uri a {{entity_type}} .
            ?uri {{entity_predicate}} "{{entity_value}}" .
        }
        LIMIT 1
        """
    query = query.replace('{{entity_type}}', entity_type)
    query = query.replace('{{entity_predicate}}', entity_predicate)
    query = query.replace('{{entity_value}}', entity_value)
    result = vivo_sparql_query(query)
    if debug:
        print query
        print result
    try:
        b = result["results"]["bindings"][0]
        uri = b['uri']['value']
        return uri
    except:
        return None

def add_award(award):
    """
    Given an award structure, generate a uri and RDF to add the award to VIVO
    """
    ardf = ""
    uri = get_vivo_uri()
    return [ardf, uri]

def get_degree_uri(code):
    """
    Given a degree code from REDCap, return the VIVO URI for the degree
    """
    uri = ""
    return uri

def add_degree(degree):
    """
    Given a degree structure, generate a uri and RDF for adding it to VIVO
    """
    uri = get_vivo_uri()
    ardf = ""
    return [ardf, uri]

def get_geo_uri(code):
    """
    Given a degree code from REDCap, return the VIVO URI for the geographic
    area
    """
    uri = ""
    return uri

def get_ustpo_patent(patent_number):
    """
    Given a patent number, use the USPTO API to return information about
    the patent and return it as a structure
    """
    patent = {}
    return patent

def add_patent(patent):
    """
    Given a patent structure, return a uri and RDF for adding the patent to VIVO
    """
    ardf = ""
    uri = get_vivo_uri()
    return [ardf, uri]

def get_service_role_uri(code):
    """
    Given a service role from REDCap, return a VIVO URI for the service role
    """
    uri = ""
    return uri

def add_service(service):
    """
    Given a service structure, return uri and RDF for adding service to VIVO
    """
    ardf = ""
    uri = get_vivo_uri()
    return [ardf, uri]


# Start here

print datetime.now(),"Start"

if len(sys.argv) > 1:
    input_file_name = str(sys.argv[1])
else:
    input_file_name = "VIVODataCollectionTo_DATA_2014-07-29_0909.csv"
file_name, file_extension = os.path.splitext(input_file_name)

add_file = codecs.open(file_name+"_add.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
sub_file = codecs.open(file_name+"_sub.rdf", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
log_file = sys.stdout
##log_file = codecs.open(file_name+"_log.txt", mode='w', encoding='ascii',
##                       errors='xmlcharrefreplace')
exc_file = codecs.open(file_name+"_exc.txt", mode='w', encoding='ascii',
                       errors='xmlcharrefreplace')
    
redcap = read_csv(input_file_name)
print datetime.now(), len(redcap), "records in survey file", input_file_name

exc_file = open("exc_file.txt", "w")
ardf = rdf_header()
srdf = rdf_header()

for row_number in sorted(redcap.keys()):
    row = redcap[row_number]

    # Check ufid and name

    ufid = row['uf_id_number']
    uri = find_entity_uri('ufVivo:UFCurrentEntity', 'ufVivo:ufid', ufid,
                          debug=True)
    if uri is None:
        print >>exc_file, "Row", row_number, "UFID", ufid, "not found"
        continue
    vivo_last_name = get_vivo_value(uri, 'foaf:lastName')
    if vivo_last_name != row['last_name']:
        print >>exc_file, "Row", row_number, "UFID", ufid, \
            "Last name in VIVO = ", vivo_last_name, "does not match survey",\
            "lastname = ", row['last_name']
        continue

    # eRACommonsId

    if row['era_commons_id'] != "":
        vivo_era_commons = get_vivo_value(uri, 'vivo:eRACommonsId')
        [add, sub] = update_data_property(uri, 'vivo:eRACommonsId', \
            vivo_era_commons, row['era_commons_id'])
        ardf = ardf + add
        srdf = srdf + sub

    # Awards

    for i in range(1,10):
        award = {}
        key = 'award_'+str(i)
        if row[key+'_sponsor'] != "":
            award['organization'] = get_vivo_uri()
            award['date'] = make_datetime(row[key+'_start_y'], \
                row[key+'_start_m'], row[key+'_start_d'])
            award['person_uri'] = uri      
            [add, award_uri] = add_award(award)
            ardf = ardf + add

    # Degrees

    for i in range(1,5):
        degree = {}
        key = 'deg_'+str(i)
        if row['degree_choice_'+str(i)] != 0:
            degree['organization'] = get_vivo_uri()
            degree['date'] = make_datetime(row[key+'_date_y'],\
                row[key+'_date_m'], row[key+'_date_d'])
            degree['field'] = row[key+'_field']
            degree['person_uri'] = uri
            degree['degree'] = get_degree_uri(row['degree_choice_'+str(i)])
            [add, degree_uri] = add_degree(degree)
            ardf = ardf + add

    # Research Overview

    if row['expert_1_overv'] != '':
        vivo_value = get_vivo_value(uri, 'vivo:researchOverview')
        [add, sub] = update_data_property(uri, 'vivo:researchOverview',\
            vivo_value, row['expert_1_overv'])
        ardf = ardf + add
        srdf = srdf + sub

    # Areas of Expertise

    for i in range(1,3):
        key = 'expert_' + str(i)
        if row[key] != "":
            concept_uri = find_entity_uri('skos:Concept', 'rdfs:label', \
                                          row[key])
            if concept_uri is not None:
                ardf = ardf + assert_resource_property(uri,
                    'vivo:hasSubjectArea', concept_uri)

    # Geographic Foci

    for i in range(1,3):
        key = 'focus_'+str(i)+'_country'
        if row[key] != "":
            geo_uri = get_geo_uri(row[key]) 
            ardf = ardf + assert_resource_property(uri,
                'vivo:hasGeographicFocus', geo_uri)

    # Patents

    for i in range(1,10):
        key = 'patent_'+str(i)+'_number'
        if row[key] != "": 
            patent = get_ustpo_patent(row[key])
            patent['person_uri'] = uri
            [add, patent_uri] = add_patent(patent)
            ardf = ardf + add
                                      
    # Editorial Roles

    for i in range(1,10):
        service = {}
        key = 'roles_'+str(i)
        if row[key+'_yn'] != 0:
            service['journal'] = find_entity_uri('bibo:Journal', 'rdfs:label', \
                                               row[key+'_journal'])
            service['start_date'] = make_datetime(row[key+'_start_y'],
                row[key+'_start_m'], row[key+'_start_d'])
            service['end_date'] = make_datetime(row[key+'_start_y'],
                row[key+'_start_m'], row[key+'_start_d'])
            service['person_uri'] = uri
            service['role'] = get_service_role_uri(row[key+'_yn'])
            [add, service_uri] = add_service(service)
            ardf = ardf + add

adrf = ardf + rdf_footer()
srdf = srdf + rdf_footer()
add_file.write(adrf)
sub_file.write(srdf)
add_file.close()
sub_file.close()
exc_file.close()

print datetime.now(),"Finished"
