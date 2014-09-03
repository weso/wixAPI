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

url_root = "http://example.com"
area_repo = AreaRepository(url_root=url_root)
ind_repo = IndicatorRepository(url_root=url_root)
obs_repo = ObservationRepository(url_root=url_root)

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
    continents = area_repo.find_continents()
    countries = area_repo.find_countries()
    continents.append(countries)
    return success(continents)


@app.route("/areas/countries")
def list_countries():
    countries = area_repo.find_countries()
    return success(countries)


@app.route("/areas/continents")
def list_continents():
    continents = area_repo.find_continents()
    return success(continents)


@app.route("/areas/<area_code>")
def show_area(area_code):
    area = area_repo.find_countries_by_code_or_income(area_code)
    if area is None:
        return area_repo.area_error(area_code)
    return success(area)


@app.route("/areas/<area_code>/countries")
def show_area_countries(area_code):
    countries = area_repo.find_countries_by_continent_or_income(area_code)
    if countries is None:
        return area_repo.area_error(area_code)
    return success(countries)


##########################################################################################
##                                     INDICATORS                                       ##
##########################################################################################

@app.route("/indicators")
def list_indicators():
    _index = ind_repo.find_indicators_index()
    subindices = ind_repo.find_indicators_sub_indexes()
    components = ind_repo.find_indicators_components()
    indicators = ind_repo.find_indicators_indicators()
    _index.append(subindices)
    _index.append(components)
    _index.append(indicators)
    return success(_index)


@app.route("/indicators/index")
def show_index():
    _index = ind_repo.find_indicators_index()
    return success(_index)

@app.route("/indicators/subindices")
def list_subindices():
    subindices = ind_repo.find_indicators_sub_indexes()
    return success(subindices)

@app.route("/indicators/components")
def list_components():
    components = ind_repo.find_indicators_components()
    return success(components)


@app.route("/indicators/primary")
def list_primary():
    primary = ind_repo.find_indicators_primary()
    return success(primary)


@app.route("/indicators/secondary")
def list_secondary():
    secondary = ind_repo.find_indicators_secondary()
    return success(secondary)


@app.route("/indicators/<indicator_code>")
def show_indicator(indicator_code):
    indicator = ind_repo.find_indicators_by_code(indicator_code)
    if indicator is None:
        return ind_repo.indicator_error(indicator_code)
    return success(indicator)


@app.route("/indicators/<indicator_code>/components")
def list_indicator_components(indicator_code):
    indicator = ind_repo.find_indicators_by_code(indicator_code)
    if indicator is None:
        return ind_repo.indicator_error(indicator_code)
    components = ind_repo.find_indicators_components(indicator)
    return success(components)


@app.route("/indicators/<indicator_code>/indicators")
def list_indicator_indicators(indicator_code):
    indicator = ind_repo.find_indicators_by_code(indicator_code)
    if indicator is None:
        return ind_repo.indicator_error(indicator_code)
    indicators = ind_repo.find_indicators_indicators(indicator)
    return success(indicators)


@app.route("/indicators/<indicator_code>/primary")
def list_indicator_primary(indicator_code):
    indicator = ind_repo.find_indicators_by_code(indicator_code)
    if indicator is None:
        return ind_repo.indicator_error(indicator_code)
    primary = ind_repo.find_indicators_primary(indicator)
    return success(primary)


@app.route("/indicators/<indicator_code>/secondary")
def list_indicator_secondary(indicator_code):
    indicator = ind_repo.find_indicators_by_code(indicator_code)
    if indicator is None:
        return ind_repo.indicator_error(indicator_code)
    secondary = ind_repo.find_indicators_secondary(indicator)
    return success(secondary)


##########################################################################################
##                                    OBSERVATIONS                                      ##
##########################################################################################
@app.route("/observations")
def list_observations():
    observations = obs_repo.find_observations()
    return observations


@app.route("/observations/<indicator_code>")
def list_observations_by_indicator(indicator_code):
    observations = obs_repo.find_observations(indicator_code)
    return observations


@app.route("/observations/<indicator_code>/<area_code>")
def list_observations_by_indicator_and_country(indicator_code, area_code):
    observations = obs_repo.find_observations(indicator_code, area_code)
    return observations


@app.route("/observations/<indicator_code>/<area_code>/<year>")
def list_observations_by_indicator_and_country_and_year(indicator_code, area_code, year):
    observations = obs_repo.find_observations(indicator_code, area_code, year)
    return observations


def success(data):
    return dumps({"success": True, "data": data})


if __name__ == "__main__":
    app.debug = True
    app.run()