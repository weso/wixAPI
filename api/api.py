##########################################################################################
##                                  INITIALISATIONS                                     ##
##########################################################################################

# Flask
from flask import Flask, jsonify
app = Flask(__name__)

# bson
from bson.json_util import dumps

# PyMongo
from pymongo import MongoClient
client = MongoClient('localhost', 9090)

# Database
db = client['webindex']

##########################################################################################
##                                        ROOT                                          ##
##########################################################################################

@app.route("/")
def index():
    return "Web Index API"
    
##########################################################################################
##                                       AREAS                                          ##
##########################################################################################

@app.route("/areas")
def list_areas():
    continents = find_continents()
    countries = find_countries()
    continents.append(countries)
    
    return success(continents)
    
@app.route("/areas/continents")
def list_continents():
    continents = find_continents()
    return success(continents)
    
@app.route("/areas/<area_code>")
def show_area(area_code):
    area = find_countries_by_code(area_code)
    
    if area is None:
        return area_error(area_code)
    
    name = area["name"]
    countries = db['areas'].find({ "area": name })
    
    if countries.count() > 0:
        area["countries"] = countries
        
    return success(area)
    
@app.route("/areas/<area_code>/countries")
def show_area_countries(area_code):
    area = find_countries_by_code(area_code)
    
    if area is None:
        return area_error(area_code)
    
    name = area["name"]
    countries = db['areas'].find({ "area": name })
    return success(countries)
    
##########################################################################################
##                                     INDICATORS                                       ##
##########################################################################################

@app.route("/indicators")
def list_indicators():
    index = find_indicators_index()
    subindices = find_indicators_subindices()
    components = find_indicators_components()
    indicators = find_indicators_indicators()
    index.append(subindices)
    index.append(components)
    index.append(indicators)
    return success(index)
    
@app.route("/indicators/index")
def show_index():
    index = find_indicators_index()
    return success(index)
    
@app.route("/indicators/subindices")
def list_subindices():
    subindices = find_indicators_subindices()
    return success(subindices)
    
@app.route("/indicators/components")
def list_components():
    components = find_indicators_components()
    return success(components)
    
@app.route("/indicators/primary")
def list_primary():
    primary = find_indicators_primary()
    return success(primary)
    
@app.route("/indicators/secondary")
def list_secondary():
    secondary = find_indicators_secondary()
    return success(secondary)
    
@app.route("/indicators/<indicator_code>")
def show_indicator(indicator_code):
    indicator = find_indicators_by_code(indicator_code)
    
    if indicator == None:
        return indicator_error(indicator_code)
    
    return success(indicator)
    
@app.route("/indicators/<indicator_code>/components")
def list_indicator_components(indicator_code):
    indicator = find_indicators_by_code(indicator_code)
    
    if indicator == None:
        return indicator_error(indicator_code)
    
    components = find_indicators_components(indicator)
    
    return success(components)
    
@app.route("/indicators/<indicator_code>/indicators")
def list_indicator_indicators(indicator_code):
    indicator = find_indicators_by_code(indicator_code)
    
    if indicator == None:
        return indicator_error(indicator_code)
    
    indicators = find_indicators_indicators(indicator)
    return success(indicators)
    
@app.route("/indicators/<indicator_code>/primary")
def list_indicator_primary(indicator_code):
    indicator = find_indicators_by_code(indicator_code)
    
    if indicator == None:
        return indicator_error(indicator_code)
    
    primary = find_indicators_primary(indicator)
    return success(primary)
    
@app.route("/indicators/<indicator_code>/secondary")
def list_indicator_secondary(indicator_code):
    indicator = find_indicators_by_code(indicator_code)
    
    if indicator == None:
        return indicator_error(indicator_code)
    
    secondary = find_indicators_secondary(indicator)
    return success(secondary)
    
##########################################################################################
##                                    OBSERVATIONS                                      ##
##########################################################################################

@app.route("/observations")
def list_observations():
    observations = find_observations()
    return observations
    
@app.route("/observations/<indicator_code>")
def list_observations_by_indicator(indicator_code):
    observations = find_observations(indicator_code)
    return observations
    
@app.route("/observations/<indicator_code>/<area_code>")
def list_observations_by_indicator_and_country(indicator_code, area_code):
    observations = find_observations(indicator_code, area_code)
    return observations
    
@app.route("/observations/<indicator_code>/<area_code>/<year>")
def list_observations_by_indicator_and_country_and_year(indicator_code, area_code, year):
    observations = find_observations(indicator_code, area_code, year)
    return observations
    
##########################################################################################
##                                 AUXILIARY FUNCTIONS                                  ##
##########################################################################################    
    
def success(data):
    return dumps({ "success": True, "data": data })
    
def error(text = ""):
    return dumps({ "success": False, "error": text }) 
    
##########################################################################################
##                              AUXILIARY AREA FUNCTIONS                                ##
##########################################################################################

def find_countries_by_code(area_code):
    area_code_upper = area_code.upper()
    area = db['areas'].find_one({ "$or": [
    									{ "iso3": area_code }, 
    									{ "iso3": area_code_upper },
    									{ "iso2": area_code }, 
    									{ "iso2": area_code_upper }, 
    									{ "name": area_code }] })
    return area
    
def find_continents():
    areas = db['areas'].find({ "area": None })
    continents = []

    for continent in areas:
        name = continent["name"]
        continent["countries"] = db['areas'].find({ "area": name })
        continents.append(continent)
        
    return continents
    
def find_countries():
    countries = db['areas'].find({ "area": { "$ne": None } })
        
    return countries
    
def area_error(area_code):
    return error("Invalid Area Code: %s" % area_code)
    
##########################################################################################
##                           AUXILIARY INDICATOR FUNCTIONS                              ##
##########################################################################################

def find_indicators_by_code(indicator_code):
    indicator_code = indicator_code.upper()
    indicator = db['indicators'].find_one({ "indicator": indicator_code })
    
    if indicator == None:
        return None
    
    children = find_indicator_children(indicator_code)
    indicator["children"] = children
    return indicator

def find_indicators_index():
    return find_indicators_by_level("Index")

def find_indicators_subindices():
    return find_indicators_by_level("Subindex")
    
def find_indicators_components(parent=None):
    return find_indicators_by_level("Component", parent)
    
def find_indicators_primary(parent = None):
    return find_indicators_by_level("Primary", parent)
    
def find_indicators_secondary(parent = None):
    return find_indicators_by_level("Secondary", parent)
    
def find_indicators_indicators(parent = None):
    primary = find_indicators_primary(parent)
    secondary = find_indicators_secondary(parent)
    primary.append(secondary)
    
    return primary
    
def find_indicators_by_level(level, parent = None):
    search = { "type": level }
    
    if parent != None:
        code = parent["indicator"]
        type = parent["type"].lower()
        filter = {}
        filter[type] = code
        search = {"$and": [search, filter]}
     
    indicators = db["indicators"].find(search)
    
    processedIndicators = []
    
    for indicator in indicators:
        code = indicator["indicator"]
    	children = find_indicator_children(code)
    	indicator["children"] = children
        processedIndicators.append(indicator)
    
    return processedIndicators
    
def find_indicator_children(indicator):
    indicators = db["indicators"].find({ "parent": indicator })
    processedIndicators = []
    
    for indicator in indicators:
        code = indicator["indicator"]
        children = find_indicator_children(code)
        indicator["children"] = children
        processedIndicators.append(indicator)
    
    return processedIndicators
    
def indicator_error(indicator_code):
    return error("Invalid Indicator Code: %s" % indicator_code)

##########################################################################################
##                          AUXILIARY OBSERVATION FUNCTIONS                             ##
##########################################################################################

def find_observations(indicator_code = None, area_code = None, year = None):
    filters = []
    
    if indicator_code != None:
    	indicator_code = indicator_code.upper()
    	
    	# Check that the indicator exists
    	indicator = db['indicators'].find_one({ "indicator": indicator_code })
    
    	if indicator == None:
        	return indicator_error(indicator_code)
    	
        filters.append({ "indicator": indicator_code })
        
    if area_code != None:
    	area_code = area_code.upper()
    	
    	# Check that the area exists
    	area = db['areas'].find_one({ "iso3": area_code })
    	
    	if area == None:
    		return area_error(area_code)
    	
        filters.append({ "area": area_code })
        
    if year != None:
        filters.append({ "year": year })
    
    search = {}
    
    if len(filters) > 0:
        search = { "$and": filters }
    
    observations = db["observations"].find(search)
    
    return success(observations)

##########################################################################################
##                                        MAIN                                          ##
##########################################################################################

if __name__ == "__main__":
    app.debug = True
    app.run()