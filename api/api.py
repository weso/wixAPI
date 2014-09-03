##########################################################################################
##                                  INITIALISATIONS                                     ##
##########################################################################################

# Flask
from flask import Flask, jsonify, request, render_template
app = Flask(__name__)

# bson
from bson.json_util import dumps

# PyMongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)

# Database
db = client['webindex']

##########################################################################################
##                                        ROOT                                          ##
##########################################################################################

@app.route("/")
def index():
  '''API Documentation'''
  return render_template('help.html')

##########################################################################################
##                                       AREAS                                          ##
##########################################################################################

@app.route("/areas")
def list_areas():
  '''List all areas (countries and continents)'''
  continents = find_continents()
  countries = find_countries()
  continents.append(countries)

  return success(continents)

@app.route("/areas/countries")
def list_countries():
    countries = find_countries()
    return success(countries)

@app.route("/areas/continents")
def list_continents():
    continents = find_continents()
    return success(continents)

@app.route("/areas/<area_code>")
def show_area(area_code):
    area = find_countries_by_code_or_income(area_code)

    if area == None:
        return area_error(area_code)

    return success(area)

@app.route("/areas/<area_code>/countries")
def show_area_countries(area_code):
    countries = find_countries_by_continent_or_income(area_code)

    if countries == None:
        return area_error(area_code)

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
##                                        YEARS                                         ##
##########################################################################################

@app.route("/years")
def list_years():
    years = db["observations"].find().distinct("year");
    years.sort()
    return success(years)

##########################################################################################
##                                 AUXILIARY FUNCTIONS                                  ##
##########################################################################################

def success(data):
    return dumps({ "success": True, "data": data })

def error(text = ""):
    return dumps({ "success": False, "error": text })

def uri(element, element_code, level):
    element["uri"] = "%s%s/%s" % (request.url_root, level, element[element_code])

##########################################################################################
##                              AUXILIARY AREA FUNCTIONS                                ##
##########################################################################################

def find_countries_by_code_or_income(area_code_or_income):
    area_code_or_income_upper = area_code_or_income.upper()
    area = db['areas'].find_one({ "$or": [
    									{ "iso3": area_code_or_income },
    									{ "iso3": area_code_or_income_upper },
    									{ "iso2": area_code_or_income },
    									{ "iso2": area_code_or_income_upper },
    									{ "name": area_code_or_income }] })

    if area == None:
        # Find if code is an income code
        countries = find_countries_by_continent_or_income(area_code_or_income_upper)
        if countries == None:
            return None
        else:
            return countries

    set_continent_countries(area)
    area_uri(area)

    return area

def find_countries_by_continent_or_income(continent_or_income):
    continent_or_income_upper = continent_or_income.upper()
    countries = db['areas'].find({ "$or": [
    										{ "area": continent_or_income },
    										{ "income": continent_or_income_upper }] })

    if countries.count() == 0:
        return None

    countryList = []

    for country in countries:

        set_continent_countries(country)
        area_uri(country)
        countryList.append(country)

    return countryList

def find_continents():
    areas = db['areas'].find({ "area": None })
    continents = []

    for continent in areas:
        set_continent_countries(continent)

        area_uri(continent)
        continents.append(continent)

    return continents

def find_countries():
    countries = db['areas'].find({ "area": { "$ne": None } })
    countryList = []

    for country in countries:
        area_uri(country)
        countryList.append(country)

    return countryList

def set_continent_countries(area):
    iso3 = area["iso3"]
    countries = db['areas'].find({ "area": iso3 })
    countryList = []

    for country in countries:
        area_uri(country)
        countryList.append(country)

    if countries.count() > 0:
        area["countries"] = countryList

def area_error(area_code):
    return error("Invalid Area Code: %s" % area_code)

def area_uri(area):
    field = "iso3" if area["iso3"] != None else "name"
    uri(area, field, "areas")

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
    indicator_uri(indicator)

    return indicator

def find_indicators_index():
    return find_indicators_by_level("Index")

def find_indicators_subindices():
    return find_indicators_by_level("Subindex")

def find_indicators_components(parent = None):
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
    	indicator_uri(indicator)
        processedIndicators.append(indicator)

    return processedIndicators

def find_indicator_children(indicator):
    indicators = db["indicators"].find({ "parent": indicator })
    processedIndicators = []

    for indicator in indicators:
        code = indicator["indicator"]
        children = find_indicator_children(code)
        indicator["children"] = children
        indicator_uri(indicator)
        processedIndicators.append(indicator)

    return processedIndicators

def indicator_error(indicator_code):
    return error("Invalid Indicator Code: %s" % indicator_code)

def indicator_uri(indicator_code):
    uri(indicator_code, "indicator", "indicators")

##########################################################################################
##                          AUXILIARY OBSERVATION FUNCTIONS                             ##
##########################################################################################

def find_observations(indicator_code = None, area_code = None, year = None):
    filters = []

    if indicator_code != None:
    	# Check that the indicator exists
    	indicatorFilter = get_indicators_by_code(indicator_code)

    	if indicatorFilter == None:
        	return indicator_error(indicator_code)

        filters.append(indicatorFilter)

    if area_code != None:
        area_filter = get_countries_by_code_name_or_income(area_code)

    	if area_filter == None:
    		return area_error(area_code)

        filters.append(area_filter)

    yearFilter = get_years(year)

    if yearFilter != None:
        filters.append(yearFilter)

    search = {}

    if len(filters) > 0:
        search = { "$and": filters }

    observations = db["observations"].find(search)
    observationList = []

    for observation in observations:
        observation_uri(observation)
        set_observation_country_and_indicator_name(observation)
        observationList.append(observation)

    return success(observationList)

def get_indicators_by_code(code):
    codes = code.upper().strip().split(",")

    for code in codes:
          # Check that the indicator exists
    	indicator = db['indicators'].find_one({ "indicator": code })

    	if indicator == None:
        	return indicator_error(code)

    return { "indicator": { "$in": codes } }

def get_countries_by_code_name_or_income(code):
    codes = code.split(",")

    countryCodes = []

    for code in codes:
        code_upper = code.upper()

        # by ISO3
        countries = db["areas"].find({ "iso3": code_upper })

        # by ISO2
        if countries == None or countries.count() == 0:
            countries = db["areas"].find({ "iso2": code_upper })

        # by name
        if countries == None or countries.count() == 0:
            countries = db["areas"].find({ "name": code })

        # by Continent

        if countries == None or countries.count() == 0:
           countries = db["areas"].find({ "area": code })

        # by Income
        if countries == None or countries.count() == 0:
           countries = db["areas"].find({ "income": code_upper })

        if countries == None or countries.count() == 0:
            return None

        for country in countries:
           iso3 = country["iso3"]
           countryCodes.append(iso3)

    return { "area": { "$in": countryCodes } }

def get_years(year):
    if year is None:
        return None

    years = year.strip().split(",")

    yearList = []

    for year in years:
        interval = year.split("-")

        if len(interval) == 1 and interval[0].isnumeric():
            yearList.append(interval[0])
        elif len(interval) == 2 and interval[0].isnumeric() and interval[1].isnumeric():
            for i in range(int(interval[0]), int(interval[1]) + 1):
                yearList.append(str(i))

    return { "year": { "$in": yearList } }

def observation_uri(observation):
    indicator_code = observation["indicator"]
    area_code = observation["area"]
    year = observation["year"]
    observation["uri"] = "%sobservations/%s/%s/%s" % (request.url_root,
                        indicator_code, area_code, year)

def set_observation_country_and_indicator_name(observation):
    indicator_code = observation["indicator"]
    area_code = observation["area"]

    indicator = db["indicators"].find_one({ "indicator": indicator_code })
    area = db["areas"].find_one({ "iso3": area_code })

    observation["indicator_name"] = indicator["name"]
    observation["area_name"] = area["name"]

##########################################################################################
##                                        MAIN                                          ##
##########################################################################################

if __name__ == "__main__":
    app.debug = True
    app.run()
