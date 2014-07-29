"""
    survey_upload.py -- Read REDCap survey data and create add and sub rdf
    for addition to VIVO

    Version 0.1 MC 2014-07-28
    --  Initial version.  
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2013, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from vivotools import read_csv
from datetime import datetime
from vivotools import get_vivo_value
from vivotools import update_data_property
from vivotools import rdf_header
from vivotools import rdf_footer

import sys
import json

print datetime.now(),"Start"
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "VIVODataCollectionTo_DATA_2014-07-29_0909.csv"
redcap = read_csv(filename)
print datetime.now(), len(redcap), "records in survey file", filename

for row_number in sorted(redcap.keys()):
    row = redcap[row_number]

    # Demographics

    ufid = row['uf_id_number']
    uri = find_vivo_uri('ufVivo:ufid', ufid)
    if uri is None:
        print >>exc_file, "Row", row_number, "UFID", ufid, "not found"
        continue
    vivo_last_name = get_vivo_value('foaf:lastName', uri)
    if vivo_last_name != row['last_name']:
        print >>exc_file, "Row", row_number, "UFID", ufid, \
            "Last name in VIVO = ", vivo_last_name, "does not match survey",
            "lastname = ", row['last_name']
        continue
    vivo_era_commons = get_vivo_value('vivo:eRACommonsId', uri)
    [add, sub] = update_data_property(uri, 'vivo:eRACommonsId', \
        vivo_era_commons, row['era_commons_id']
    ardf = ardf + add
    srdf = srdf + sub

    # Awards

    for i in range(1,10):
        award = {}
        key = 'award_'+str(i)
        if row[key+'_sponsor'] != "":
            award['organization'] = get_vivo_uri()
            award['date'] = datetime(row[key+'_start_y'], row[key+'_start_m'],
                row[key+'_start_d'])
            award['person_uri'] = uri      
            [add, sub] = add_award(award)
            ardf = ardf + add
            srdf = srdf + sub

    # Degrees

    for i in range(1,5):
        degree = {}
        key = 'deg_'+str(i)
        if row['degree_'+str(i)+'_choice'] != 0:
            degree['organization'] = get_vivo_uri()
            degree['date'] = datetime(row[key+'_start_y'], row[key+'_start_m'],
                row[key+'_start_d'])
            degree['field'] = row[key+'_field']
            degree['person_uri'] = uri
            degree['degree'] = degree_type(row['degree_'+str(i)+'_choice'])
            [add, sub] = add_degree(degree)
            ardf = ardf + add
            srdf = srdf + sub

    # Areas of Expertise

    for i in range(1,3):
        key = 'expert_'+str(i)
        if row[key] != "":
            concept_uri = get_concept_uri(row[key]) 
            ardf = ardf + assert_resource_property(uri, 'vivo:hasSubjectArea',
                        concept_uri)

    # Geographic Foci

    # Patents

    # Editorial Roles
    

print datetime.now(),"Finished"
