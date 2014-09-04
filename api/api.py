##########################################################################################
##                                  INITIALISATIONS                                     ##
##########################################################################################

# Flask
from flask import Flask, jsonify, request, render_template
app = Flask(__name__)
from infrastructure.mongo_repos.area_repository import AreaRepository
from infrastructure.mongo_repos.indicator_repository import IndicatorRepository
from infrastructure.mongo_repos.observation_repository import ObservationRepository

# bson
from bson.json_util import dumps

##########################################################################################
##                                        ROOT                                          ##
##########################################################################################

@app.route("/")
def index():
    """API Documentation"""
    return render_template('help.html')

##########################################################################################
##                                       AREAS                                          ##
##########################################################################################

@app.route("/areas")
def list_areas():
    """List all areas (countries and continents)"""
    areas = AreaRepository(url_root=request.url_root).find_areas()

    return dumps(areas)


@app.route("/areas/countries")
def list_countries():
    countries = AreaRepository(url_root=request.url_root).find_countries()
    return dumps(countries)


@app.route("/areas/continents")
def list_continents():
    continents = AreaRepository(url_root=request.url_root).find_continents()
    return dumps(continents)


@app.route("/areas/<area_code>")
def show_area(area_code):
    area = AreaRepository(url_root=request.url_root).find_countries_by_code_or_income(area_code)
    return dumps(area)


@app.route("/areas/<area_code>/countries")
def show_area_countries(area_code):
    countries = AreaRepository(url_root=request.url_root).find_countries_by_continent_or_income(area_code)
    return dumps(countries)


##########################################################################################
##                                     INDICATORS                                       ##
##########################################################################################

@app.route("/indicators")
def list_indicators():
    indicators = IndicatorRepository(url_root=request.url_root).find_indicators()

    return dumps(indicators)


@app.route("/indicators/index")
def show_index():
    _index = IndicatorRepository(url_root=request.url_root).find_indicators_index()
    return dumps(_index)

@app.route("/indicators/subindices")
def list_subindices():
    subindices = IndicatorRepository(url_root=request.url_root).find_indicators_sub_indexes()
    return dumps(subindices)

@app.route("/indicators/components")
def list_components():
    components = IndicatorRepository(url_root=request.url_root).find_indicators_components()
    return dumps(components)


@app.route("/indicators/primary")
def list_primary():
    primary = IndicatorRepository(url_root=request.url_root).find_indicators_primary()
    return dumps(primary)


@app.route("/indicators/secondary")
def list_secondary():
    secondary = IndicatorRepository(url_root=request.url_root).find_indicators_secondary()
    return dumps(secondary)


@app.route("/indicators/<indicator_code>")
def show_indicator(indicator_code):
    indicator = IndicatorRepository(url_root=request.url_root).find_indicators_by_code(indicator_code)
    return dumps(indicator)


@app.route("/indicators/<indicator_code>/components")
def list_indicator_components(indicator_code):
    indicator = IndicatorRepository(url_root=request.url_root).find_indicators_by_code(indicator_code)

    if indicator["success"] is False:
        return dumps(indicator)

    components = IndicatorRepository(url_root=request.url_root).find_indicators_components(indicator["data"])
    return dumps(components)


@app.route("/indicators/<indicator_code>/indicators")
def list_indicator_indicators(indicator_code):
    indicator = IndicatorRepository(url_root=request.url_root).find_indicators_by_code(indicator_code)

    if indicator["success"] is False:
        return dumps(indicator)

    indicators = IndicatorRepository(url_root=request.url_root).find_indicators_indicators(indicator["data"])
    return dumps(indicators)


@app.route("/indicators/<indicator_code>/primary")
def list_indicator_primary(indicator_code):
    indicator = IndicatorRepository(url_root=request.url_root).find_indicators_by_code(indicator_code)

    if indicator["success"] is False:
        return dumps(indicator)

    primary = IndicatorRepository(url_root=request.url_root).find_indicators_primary(indicator["data"])
    return dumps(primary)


@app.route("/indicators/<indicator_code>/secondary")
def list_indicator_secondary(indicator_code):
    indicator = IndicatorRepository(url_root=request.url_root).find_indicators_by_code(indicator_code)

    if indicator["success"] is False:
        return dumps(indicator)

    secondary = IndicatorRepository(url_root=request.url_root).find_indicators_secondary(indicator["data"])
    return dumps(secondary)


##########################################################################################
##                                    OBSERVATIONS                                      ##
##########################################################################################
@app.route("/observations")
def list_observations():
    observations = ObservationRepository(url_root=request.url_root).find_observations()
    return dumps(observations)


@app.route("/observations/<indicator_code>")
def list_observations_by_indicator(indicator_code):
    observations = ObservationRepository(url_root=request.url_root).find_observations(indicator_code)
    return dumps(observations)


@app.route("/observations/<indicator_code>/<area_code>")
def list_observations_by_indicator_and_country(indicator_code, area_code):
    observations = ObservationRepository(url_root=request.url_root).find_observations(indicator_code, area_code)
    return dumps(observations)


@app.route("/observations/<indicator_code>/<area_code>/<year>")
def list_observations_by_indicator_and_country_and_year(indicator_code, area_code, year):
    observations = ObservationRepository(url_root=request.url_root).find_observations(indicator_code, area_code, year)
    return dumps(observations)

##########################################################################################
##                                        MAIN                                          ##
##########################################################################################

if __name__ == "__main__":
    app.debug = True
    app.run()