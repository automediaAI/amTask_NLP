import requests
from wikidata2df import wikidata2df

location_query = """
SELECT DISTINCT ?item ?itemLabel ?description ?sitelinks WHERE {
  ?item wdt:P31 ?typeOfLoc .
  ?item wikibase:sitelinks ?sitelinks .
  VALUES ?superclasses { wd:Q486972 wd:Q6256 }
  ?typeOfLoc wdt:P279 * ?superclasses . hint:Prior hint:gearing "forward" .
  VALUES ?label { rdfs:label skos:altLabel }
  ?item ?label "%(locationName)s"@en .
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" .
    ?item rdfs:label ?itemLabel .
    ?item schema:description ?description .
  }
} ORDER BY DESC (?sitelinks)
"""

person_query = """
SELECT ?item ?itemLabel ?fow ?fowLabel ?description ?sitelinks WHERE {
  ?item wdt:P31 wd:Q5 .
  ?item wikibase:sitelinks ?sitelinks .
  ?item ?label "%(personName)s"@en .
  OPTIONAL {?item wdt:P101 ?fow} .
  VALUES ?label { rdfs:label skos:altLabel }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" .
    ?item rdfs:label ?itemLabel .
    ?item schema:description ?description .
    ?fow rdfs:label ?fowLabel .
  }
} ORDER BY DESC (?sitelinks)
"""

org_query = """
SELECT DISTINCT ?item ?itemLabel ?description ?sitelinks WHERE {
  ?item wdt:P31 ?typeOfOrg .
  ?item wikibase:sitelinks ?sitelinks .
  VALUES ?superclasses { wd:Q43229 wd:Q340169 }
  ?typeOfOrg wdt:P279 * ?superclasses . hint:Prior hint:gearing "forward" .
  VALUES ?label { rdfs:label skos:altLabel }
  ?item ?label "%(orgName)s"@en .
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" .
    ?item rdfs:label ?itemLabel .
    ?item schema:description ?description .
  }
} ORDER BY DESC (?sitelinks)
"""

# VALUES ?superclasses { wd:Q15401930 }
# testing more superclasses
product_query = """
SELECT DISTINCT ?item ?itemLabel ?description ?sitelinks WHERE {
  ?item wdt:P31 ?typeOfLoc .
  ?item wikibase:sitelinks ?sitelinks .
  VALUES ?superclasses { wd:Q15401930 wd:Q17537576 }
  ?typeOfLoc wdt:P279 * ?superclasses . hint:Prior hint:gearing "forward" .
  VALUES ?label { rdfs:label skos:altLabel }
  ?item ?label "%(prodName)s"@en .
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" .
    ?item rdfs:label ?itemLabel .
    ?item schema:description ?description .
  }
} ORDER BY DESC (?sitelinks)
"""

event_query = """
SELECT DISTINCT ?item ?itemLabel ?description ?sitelinks WHERE {
  ?item wdt:P31 ?typeOfLoc .
  ?item wikibase:sitelinks ?sitelinks .
  VALUES ?superclasses { wd:Q1656682}
  ?typeOfLoc wdt:P279 * ?superclasses . hint:Prior hint:gearing "forward" .
  VALUES ?label { rdfs:label skos:altLabel }
  ?item ?label "%(eventName)s"@en .
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en" .
    ?item rdfs:label ?itemLabel .
    ?item schema:description ?description .
  }
} ORDER BY DESC (?sitelinks)
"""


def wikidata_sparql_get_generic(item_name, item_type):
    sparql_query = ""
    if item_type == "GPE":
        sparql_query = location_query % {'locationName': item_name}
    elif item_type == "PERSON":
        sparql_query = person_query % {'personName': item_name}
    elif item_type == "ORG":
        sparql_query = org_query % {'orgName': item_name}
    elif item_type == "EVENT":
        sparql_query = event_query % {'eventName': item_name}
    elif item_type in ["PRODUCT", "WORK_OF_ART"]:
        sparql_query = product_query  % {'prodName': item_name}
    else:
        print("item_type is invalid, returning blank")
        return ""

    # print(sparql_query) # debug

    # Returns a Pandas DataFrame
    items_dataframe = wikidata2df(sparql_query)
    # print(items_dataframe) # debug

    if items_dataframe.empty:
        print("nothing returned from wikidata, returning blank")
        return ""

    if 'description' in items_dataframe.columns:
        # remove None values in the description
        # removing null values will help reduce extra results from 
        items_dataframe = items_dataframe[~items_dataframe['description'].isnull()]
    else:
        print("description field is empty, returning blank")
        return ""

    if items_dataframe.empty:
        print("no descriptions found in any entry, returning blank")
        return ""

    if 'description' in items_dataframe.columns:
        # remove None values in the description
        # removing null values will help reduce extra results from 
        items_dataframe = items_dataframe[items_dataframe.description != "Wikimedia disambiguation page"]
    else:
        print("description field is empty, returning blank")
        return ""

    if items_dataframe.empty:
        print("no descriptions found in any entry, returning blank")
        return ""

    #resets index of the dataframe so if 0th value is removed, 1th will become the new 0th
    items_dataframe = items_dataframe.reset_index(drop=True)

    # print(items_dataframe) # debug
    # print(items_dataframe.at[0, 'itemLabel'], items_dataframe.at[0, 'description']) # debug
    return items_dataframe


def wikidata_sparql_get_location(location_name):
    # multiline f-string using the variable inline
    location_query = """
    SELECT DISTINCT ?item ?itemLabel ?description WHERE {
      ?item wdt:P31 ?typeOfLoc .
      VALUES ?superclasses { wd:Q486972 wd:Q6256 }
      ?typeOfLoc wdt:P279 ?superclasses .
      VALUES ?label { rdfs:label skos:altLabel }
      ?item ?label "%(locationName)s"@en .
      SERVICE wikibase:label { 
        bd:serviceParam wikibase:language "en" .
        ?item rdfs:label ?itemLabel .
        ?item schema:description ?description .
      }
    }
    """ % {'locationName': location_name}

    # print(location_query) # debug

    # Returns a Pandas DataFrame
    locations_dataframe = wikidata2df(location_query)
    # print(locations_dataframe) # debug

    if locations_dataframe.empty:
        print("locations_dataframe is empty 2")
        return ""

    if 'description' in locations_dataframe.columns:
        # remove None values in the description
        # removing null values will help reduce extra results from 
        locations_dataframe = locations_dataframe[~locations_dataframe['description'].isnull()]
    else:
        print("description field is empty, returning blank")
        return ""

    if locations_dataframe.empty:
        print("locations_dataframe is empty 2")
        return ""

    #resets index of the dataframe so if 0th value is removed, 1th will become the new 0th
    locations_dataframe = locations_dataframe.reset_index(drop=True)

    # print(locations_dataframe) # debug
    # print(locations_dataframe.at[0, 'itemLabel'], locations_dataframe.at[0, 'description']) # debug
    return locations_dataframe


def wikidata_sparql_get_person(person_name):
    # multiline f-string using the variable inline
    person_query = """
    SELECT ?item ?itemLabel ?fow ?fowLabel ?description WHERE {
      ?item wdt:P31 wd:Q5.
      ?item ?label "%(personName)s"@en .
      OPTIONAL {?item wdt:P101 ?fow} .
      VALUES ?label { rdfs:label skos:altLabel }
      SERVICE wikibase:label { 
        bd:serviceParam wikibase:language "en" .
        ?item rdfs:label ?itemLabel .
        ?item schema:description ?description .
        ?fow rdfs:label ?fowLabel .
      }
    }
    """ % {'personName': person_name}

    # print(person_query) # debug

    # Returns a Pandas DataFrame
    persons_dataframe = wikidata2df(person_query)
    # print(persons_dataframe) # debug

    if persons_dataframe.empty:
        print("persons_dataframe is empty 2")
        return ""

    if 'description' in persons_dataframe.columns:
        # remove None values in the description
        # removing null values will help reduce extra results from 
        persons_dataframe = persons_dataframe[~persons_dataframe['description'].isnull()]
    else:
        print("description field is empty, returning blank")
        return ""

    if persons_dataframe.empty:
        print("persons_dataframe is empty 2")
        return ""

    #resets index of the dataframe so if 0th value is removed, 1th will become the new 0th
    persons_dataframe = persons_dataframe.reset_index(drop=True)

    # print(persons_dataframe) # debug
    # print(persons_dataframe.at[0, 'itemLabel'], persons_dataframe.at[0, 'description']) # debug
    return persons_dataframe


def wikidata_sparql_get_org(org_name):
    # multiline f-string using the variable inline
    org_query = """
    SELECT DISTINCT ?item ?itemLabel ?description WHERE {
      ?item wdt:P31 ?typeOfOrg .
      VALUES ?superclasses { wd:Q43229 }
      ?typeOfOrg wdt:P279 ?superclasses .
      VALUES ?label { rdfs:label skos:altLabel }
      ?item ?label "%(orgName)s"@en .
      SERVICE wikibase:label { 
        bd:serviceParam wikibase:language "en" .
        ?item rdfs:label ?itemLabel .
        ?item schema:description ?description .
      }
    }
    """ % {'orgName': org_name}

    # Returns a Pandas DataFrame
    orgs_dataframe = wikidata2df(org_query)
    # print(orgs_dataframe) # debug

    if orgs_dataframe.empty:
        print("orgs_dataframe is empty 1")
        return ""

    if 'description' in orgs_dataframe.columns:
        # remove None values in the description
        # removing null values will help reduce extra results from 
        orgs_dataframe = orgs_dataframe[~orgs_dataframe['description'].isnull()]
    else:
        print("description field is empty, returning blank")
        return ""

    if orgs_dataframe.empty:
        print("orgs_dataframe is empty 2")
        return ""

    #resets index of the dataframe so if 0th value is removed, 1th will become the new 0th
    orgs_dataframe = orgs_dataframe.reset_index(drop=True)

    # print(orgs_dataframe) # debug
    # print(orgs_dataframe.at[0, 'itemLabel'], orgs_dataframe.at[0, 'description']) # debug
    return orgs_dataframe


def search_wikidata(string):
    """
    Query the Wikidata API using the wbsearchentities function.
    Return the concept ID of the first search result.
    Docs - 
    https://www.mediawiki.org/wiki/API:Main_page
    https://www.wikidata.org/w/api.php?action=help&modules=main
    https://www.mediawiki.org/w/api.php?action=help&modules=query
    https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bsearch
    https://www.wikidata.org/w/api.php?action=help&modules=wbsearchentities

    Samples - 
    https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=
    https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&titles=South%20Carolina&languages=en&format=json
    https://www.wikidata.org/w/api.php?action=query&list=search&format=json&srsearch=New+York+Landmarks+Preservation+Commission
    https://www.wikidata.org/w/api.php?action=query&list=search&format=json&srqiprofile=classic&srsearch=India

    Works better - 
    https://www.wikidata.org/w/api.php?action=query&list=search&format=json&srqiprofile=popular_inclinks_pv&srsearch=India
    https://www.wikidata.org/w/api.php?action=query&list=search&format=json&srqiprofile=popular_inclinks_pv&srsearch=New+York+Landmarks+Preservation+Commission

    Simple and works - 
    https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=CNN
    https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=India
    https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=south%20carolina

    Fails - 
    https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=Henry Castel
    https://www.wikidata.org/w/api.php?action=query&list=search&format=json&prop=categories&srsearch=India

    Inspired by https://github.com/samvanstroud/wikipeople/blob/master/wikipeople/wikipeople.py
    """
  
    query = 'https://www.wikidata.org/w/api.php'
    query += '?action=wbsearchentities&language=en&format=json&limit=1&search='
    # query += '?action=query&list=search&format=json&srsearch='
    # query += '?action=query&list=search&format=json&srqiprofile=popular_inclinks_pv&srsearch='
    query += string
  
    res = requests.get(query).json()

    if len(res['search']) == 0:
        print('Wikidata wbsearchentities search failed for ', string)
        print('Trying alt search')

        query = 'https://www.wikidata.org/w/api.php'
        query += '?action=query&list=search&format=json&srqiprofile=popular_inclinks_pv&srsearch='
        query += string

        res = requests.get(query).json()
  
        if res['query']['searchinfo']['totalhits'] == 0:
          print('Wikidata general search also failed for ', string)
          print('returning blank result')
          return ""
        return res['query']['search'][0]['snippet']
    return res['search'][0]['description']
