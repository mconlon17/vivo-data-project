"""
    survey_upload.py -- Read REDCap survey data and create add and sub rdf
    for addition to VIVO

    Version 0.1 MC 2014-07-28
    --  Initial version.
    Version 0.2 MC 2014-07-31
    --  Demographics, eracommons, degrees, overview, concepts, service are
        done.
    Version 0.3 MC 2014-08-09
    -- Geo Foci added

    To Do:
    Awards and Patents.
    
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
    Given three strings which should have a year, month and a day,
    create integer values and return a datetime. Handle empty strings
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
            {?uri {{entity_predicate}} "{{entity_value}}" .}
            UNION
            {?uri {{entity_predicate}} "{{entity_value}}"^^<http://www.w3.org/2001/XMLSchema#string> .}
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
    degrees = {
        "49": "http://vivoweb.org/ontology/degree/academicDegree4",
        "47": "http://vivoweb.org/ontology/degree/academicDegree33",
        "51":  "http://vivoweb.org/ontology/degree/academicDegree1",
        "61": "http://vivoweb.org/ontology/degree/academicDegree113",
        "71": "http://vivoweb.org/ontology/degree/academicDegree117",
        "95": "http://vivoweb.org/ontology/degree/academicDegree71",
        "86": "http://vivo.ufl.edu/individual/n128082",
        "149": "http://vivoweb.org/ontology/degree/academicDegree77",
        "109": "http://vivoweb.org/ontology/degree/academicDegree98",
        "142": "http://vivoweb.org/ontology/degree/academicDegree96",
        "146": "http://vivoweb.org/ontology/degree/academicDegree55",
        "147": "http://vivoweb.org/ontology/degree/academicDegree43"
        }
    uri = degrees.get(code, None)
    return uri

def add_degree(degree):
    """
    Given a degree structure, generate a uri and RDF for adding it to VIVO
    """
    from vivotools import add_dti
    from vivotools import assert_resource_property
    from vivotools import assert_data_property
    from vivotools import untag_predicate
    ardf = ""
    uri = None

    if degree.get('person_uri', None) is not None and \
       degree.get('degree_uri', None) is not None:
        uri = get_vivo_uri()
        ardf = ardf + assert_resource_property(uri, 'rdfs:type',
            untag_predicate('vivo:EducationalTraining'))
        ardf = ardf + assert_resource_property(uri, 'vivo:educationalTrainingOf',
                                               degree['person_uri'])
        ardf = ardf + assert_resource_property(uri, 'vivo:degreeEarned',
                                               degree['degree_uri'])
        if degree.get('org_uri', None) is not None:
            ardf = ardf + assert_resource_property(uri,
                'vivo:trainingAtOrganization', degree['org_uri'])

        if degree.get('field', None) is not None:
            ardf = ardf + assert_data_property(uri, 'vivo:majorField',
                                               degree['field'])
        if degree.get('date', None) is not None:
            [add, dti_uri] = add_dti({'start': None,
                                      'end': degree['date']})
            ardf = ardf + add
            ardf = ardf + assert_resource_property(uri, 'vivo:dateTimeInterval',
                                                   dti_uri)
    return [ardf, uri]

def get_geo_uri(code):
    """
    Given a geo code from REDCap, return the VIVO URI for the geographic
    area
    """
    geo_names = {
        "1": "Alabama",
        "2": "Alaska",
        "3": "Arizona",
        "4": "Arkansas",
        "5": "California",
        "6": "Colorado",
        "7": "Connecticut",
        "8": "Delaware",
        "9": "Florida",
        "10": "Georgia",
        "11": "Hawaii",
        "12": "Idaho",
        "13": "Illinois",
        "14": "Indiana",
        "15": "Iowa",
        "16": "Kansas",
        "17": "Kentucky",
        "18": "Louisiana",
        "19": "Maine",
        "20": "Maryland",
        "21": "Massachusetts",
        "22": "Michigan",
        "23": "Minnesota",
        "24": "Mississippi",
        "25": "Missouri",
        "26": "Montana",
        "27": "Nebraska",
        "28": "Nevada",
        "29": "New Hampshire",
        "30": "New Jersey",
        "31": "New Mexico",
        "32": "New York",
        "33": "North Carolina",
        "34": "North Dakota",
        "35": "Ohio",
        "36": "Oklahoma",
        "37": "Oregon",
        "38": "Pennsylvania",
        "39": "Rhode Island",
        "40": "South Carolina",
        "41": "South Dakota",
        "42": "Tennessee",
        "43": "Texas",
        "44": "Utah",
        "45": "Vermont",
        "46": "Virginia",
        "47": "Washington",
        "48": "West Virginia",
        "49": "Wisconsin",
        "50": "Wyoming",
        "51": "District of Columbia",
        "52": "American Samoa",
        "53": "Guam",
        "54": "Northern Mariana Islands",
        "55": "Puerto Rico",
        "56": "U.S. Virgin Islands",
        "57": "Afghanistan",
        "58": "Akrotiri",
        "59": "Albania",
        "60": "Algeria",
        "61": "American Samoa",
        "62": "Andorra",
        "63": "Angola",
        "64": "Anguilla",
        "65": "Antarctica",
        "66": "Antigua and Barbuda",
        "67": "Argentina",
        "68": "Armenia",
        "69": "Aruba",
        "70": "Ashmore and Cartier Islands",
        "71": "Australia",
        "72": "Austria",
        "73": "Azerbaijan",
        "74": "Bahamas",
        "75": "Bahrain",
        "76": "Bangladesh",
        "77": "Barbados",
        "78": "Bassas da India",
        "79": "Belarus",
        "80": "Belgium",
        "81": "Belize",
        "82": "Benin",
        "83": "Bermuda",
        "84": "Bhutan",
        "85": "Bolivia",
        "86": "Bosnia and Herzegovina",
        "87": "Botswana",
        "88": "Bouvet Island",
        "89": "Brazil",
        "90": "British Indian Ocean Territory",
        "91": "British Virgin Islands",
        "92": "Brunei",
        "93": "Bulgaria",
        "94": "Burkina Faso",
        "95": "Burma",
        "96": "Burundi",
        "97": "Cambodia",
        "98": "Cameroon",
        "99": "Canada",
        "100": "Cape Verde",
        "101": "Cayman Islands",
        "102": "Central African Republic",
        "103": "Chad",
        "104": "Chile",
        "105": "China",
        "106": "Christmas Island",
        "107": "Clipperton Island",
        "108": "Cocos (Keeling) Islands",
        "109": "Colombia",
        "110": "Comoros",
        "308": "Republic of the Congo",
        "111": "Cook Islands",
        "112": "Coral Sea Islands",
        "113": "Costa Rica",
        "114": "Cote d'Ivoire",
        "115": "Croatia",
        "116": "Cuba",
        "117": "Cyprus",
        "118": "Czech Republic",
        "119": "Denmark",
        "120": "Dhekelia",
        "121": "Djibouti",
        "122": "Dominica",
        "123": "Dominican Republic",
        "124": "Ecuador",
        "125": "Egypt",
        "126": "El Salvador",
        "127": "Equatorial Guinea",
        "128": "Eritrea",
        "129": "Estonia",
        "130": "Ethiopia",
        "131": "Europa Island",
        "132": "Falkland Islands (Islas Malvinas)",
        "133": "Faroe Islands",
        "134": "Fiji",
        "135": "Finland",
        "136": "France",
        "137": "French Guiana",
        "138": "French Polynesia",
        "139": "French Southern and Antarctic Lands",
        "140": "Gabon",
        "309": "The Gambia",
        "141": "Gaza Strip",
        "142": "Georgia",
        "143": "Germany",
        "144": "Ghana",
        "145": "Gibraltar",
        "146": "Glorioso Islands",
        "147": "Greece",
        "148": "Greenland",
        "149": "Grenada",
        "150": "Guadeloupe",
        "151": "Guam",
        "152": "Guatemala",
        "153": "Guernsey",
        "154": "Guinea",
        "155": "Guinea-Bissau",
        "156": "Guyana",
        "157": "Haiti",
        "158": "Heard Island and McDonald Islands",
        "159": "Holy See (Vatican City)",
        "160": "Honduras",
        "161": "Hong Kong",
        "162": "Hungary",
        "163": "Iceland",
        "164": "India",
        "165": "Indonesia",
        "166": "Iran",
        "167": "Iraq",
        "168": "Ireland",
        "169": "Isle of Man",
        "170": "Israel",
        "171": "Italy",
        "172": "Jamaica",
        "173": "Jan Mayen",
        "174": "Japan",
        "175": "Jersey",
        "176": "Jordan",
        "177": "Juan de Nova Island",
        "178": "Kazakhstan",
        "179": "Kenya",
        "180": "Kiribati",
        "310": "Korea": "South",
        "181": "Kuwait",
        "182": "Kyrgyzstan",
        "183": "Laos",
        "184": "Latvia",
        "185": "Lebanon",
        "186": "Lesotho",
        "187": "Liberia",
        "188": "Libya",
        "189": "Liechtenstein",
        "190": "Lithuania",
        "191": "Luxembourg",
        "192": "Macau",
        "193": "Macedonia",
        "194": "Madagascar",
        "195": "Malawi",
        "196": "Malaysia",
        "197": "Maldives",
        "198": "Mali",
        "199": "Malta",
        "200": "Marshall Islands",
        "201": "Martinique",
        "202": "Mauritania",
        "203": "Mauritius",
        "204": "Mayotte",
        "205": "Mexico",
        "311": "Federated States of Micronesia",
        "206": "Moldova",
        "207": "Monaco",
        "208": "Mongolia",
        "209": "Montserrat",
        "210": "Morocco",
        "211": "Mozambique",
        "212": "Namibia",
        "213": "Nauru",
        "214": "Navassa Island",
        "215": "Nepal",
        "216": "Netherlands",
        "217": "Netherlands Antilles",
        "218": "New Caledonia",
        "219": "New Zealand",
        "220": "Nicaragua",
        "221": "Niger",
        "222": "Nigeria",
        "223": "Niue",
        "224": "Norfolk Island",
        "225": "Northern Mariana Islands",
        "226": "Norway",
        "227": "Oman",
        "228": "Pakistan",
        "229": "Palau",
        "230": "Panama",
        "231": "Papua New Guinea",
        "232": "Paracel Islands",
        "233": "Paraguay",
        "234": "Peru",
        "235": "Philippines",
        "236": "Pitcairn Islands",
        "237": "Poland",
        "238": "Portugal",
        "239": "Puerto Rico",
        "240": "Qatar",
        "241": "Reunion",
        "242": "Romania",
        "243": "Russia",
        "244": "Rwanda",
        "245": "Saint Helena",
        "246": "Saint Kitts and Nevis",
        "247": "Saint Lucia",
        "248": "Saint Pierre and Miquelon",
        "249": "Saint Vincent and the Grenadines",
        "250": "Samoa",
        "251": "San Marino",
        "252": "Sao Tome and Principe",
        "253": "Saudi Arabia",
        "254": "Senegal",
        "255": "Serbia and Montenegro",
        "256": "Seychelles",
        "257": "Sierra Leone",
        "258": "Singapore",
        "259": "Slovakia",
        "260": "Slovenia",
        "261": "Solomon Islands",
        "262": "Somalia",
        "263": "South Africa",
        "264": "South Georgia and the South Sandwich Islands",
        "265": "Spain",
        "266": "Spratly Islands",
        "267": "Sri Lanka",
        "268": "Sudan",
        "269": "Suriname",
        "270": "Svalbard",
        "271": "Swaziland",
        "272": "Sweden",
        "273": "Switzerland",
        "274": "Syria",
        "275": "Taiwan",
        "276": "Tajikistan",
        "277": "Tanzania",
        "278": "Thailand",
        "279": "Timor-Leste",
        "280": "Togo",
        "281": "Tokelau",
        "282": "Tonga",
        "283": "Trinidad and Tobago",
        "284": "Tromelin Island",
        "285": "Tunisia",
        "286": "Turkey",
        "287": "Turkmenistan",
        "288": "Turks and Caicos Islands",
        "289": "Tuvalu",
        "290": "Uganda",
        "291": "Ukraine",
        "292": "United Arab Emirates",
        "293": "United Kingdom",
        "294": "United States",
        "295": "Uruguay",
        "296": "Uzbekistan",
        "297": "Vanuatu",
        "298": "Venezuela",
        "299": "Vietnam",
        "300": "Virgin Islands",
        "301": "Wake Island",
        "302": "Wallis and Futuna",
        "303": "West Bank",
        "304": "Western Sahara",
        "305": "Yemen",
        "306": "Zambia",
        "307": "Zimbabwe"
    }
    geo_name = geo_names.get(code, None)
    if code is None:
        return None
    elif code <= 51:
        uri = find_vivo_uri('vivo:StateOrProvince', 'rdfs:label', geo_name)
    else:
        uri = find_vivo_uri('vivo:Country', 'rdfs:label', geo_name)
    return uri

def get_ustpo_patent(patent_number):
    """
    Given a patent number, use the USPTO API to return information about
    the patent and return it as a structure
    """
    patent = {'patent_number': patent_number}
    return patent

def add_patent(patent):
    """
    Given a patent structure, return a uri and RDF for adding the patent to VIVO
    Needs to add patent and then an authorship connecting the patent to a person
    """
    ardf = ""
    patent_uri = get_vivo_uri()
    patent['patent_uri'] = patent_uri
    return [ardf, patent_uri]

def get_service_role(code):
    """
    Given a service role from REDCap, return a VIVO URI for the service role
    """
    roles = {
        "2": "Editor",
        "3": "Associate Editor",
        "4": "Reviewer",
        }
    role = roles.get(code, None)
    return role

def add_service(service):
    """
    Given a service structure, return uri and RDF for adding service to VIVO
    """
    from vivotools import add_dti
    from vivotools import assert_resource_property
    from vivotools import assert_data_property
    from vivotools import untag_predicate
    ardf = ""
    uri = get_vivo_uri()
    ardf = ardf + assert_resource_property(uri, 'rdfs:type',
        untag_predicate('vivo:ServiceProviderRole'))
    ardf = ardf + assert_resource_property(uri, 'vivo:serviceProviderRoleOf',
                                           service['person_uri'])
    ardf = ardf + assert_resource_property(uri, 'vivo:RoleIn',
                                           service['org_uri'])
    ardf = ardf + assert_data_property(uri, 'rdfs:label', service['role'])
    [add, dti_uri] = add_dti({'start': service['start_date'],
                              'end': service['end_date']})
    ardf = ardf + add
    ardf = ardf + assert_resource_property(uri, 'vivo:dateTimeInterval',
                                           dti_uri)
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
geo_codes = read_csv('geo_codes.txt')
geo_names = {}
for row_number,row in geo_codes.items():
    geo_names[row['code']] = row['geo_name']
redcap = read_csv(input_file_name)
print datetime.now(), len(redcap), "records in survey file", input_file_name

exc_file = open("exc_file.txt", "w")
ardf = rdf_header()
srdf = rdf_header()

for row_number in sorted(redcap.keys()):
    row = redcap[row_number]
    print json.dumps(row, indent=4)

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
        if row['degree_choice_'+str(i)] != "":
            degree['org_uri'] = find_entity_uri('foaf:Organization',
                'rdfs:label', row[key+'_place'], debug=True)
            degree['date'] = make_datetime(row[key+'_date_y'],\
                row[key+'_date_m'], row[key+'_date_d'])
            degree['field'] = row[key+'_field']
            degree['person_uri'] = uri
            degree['degree_uri'] = get_degree_uri(row['degree_choice_'+str(i)])
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
            print add

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
        if row[key+'_yn'] != "1" and row[key+'_yn'] != "":
            service['org_uri'] = find_entity_uri('bibo:Journal', 'rdfs:label', \
                                               row[key+'_journal'], debug=True)
            service['start_date'] = make_datetime(row[key+'_start_y'],
                row[key+'_start_m'], row[key+'_start_d'])
            service['end_date'] = make_datetime(row[key+'_start_y'],
                row[key+'_start_m'], row[key+'_start_d'])
            service['person_uri'] = uri
            service['role'] = get_service_role(row[key+'_yn'])
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
