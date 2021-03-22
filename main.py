"""
call mapbox api
"""
import requests
import os
import json

ENV_VAR="MAPBOX_API_TOKEN"
GEOCODING_ENDPOINT_TEMPORARY = "geocoding/v5/mapbox.places"
GEOCODING_ENDPOINT_PERMANENT = "geocoding/v5/mapbox.places-permanent"

class MapboxGeocoder():
    """
    encapsulates api calling for MapBox geocoder api
    """

    def __init__(self, endpoint=None):
        """
        intitialize object
        :param endpoint: mapbox API endpoint.  e.g. temporary vs permanent
        """
        self.token=self.get_token()
        self.endpoint = endpoint if endpoint else GEOCODING_ENDPOINT_TEMPORARY

    def geocode(self,query):
        """
        pass query to gecoder api
        :param query: unparsed address
        :return: response object from HTTP GET request
        """
        return call_mapbox_endpoint(query, self.token, self.endpoint)

    def get_token(self):
        """
        get api token from environment variable
        :return: api token
        """
        return get_token()

    def get_clean_address(self, query):
        """
        get a dictionary with address components from reponse
        :param query: unparsed address
        :return: dictionary of clean address components
        """
        response = call_mapbox_endpoint(query, self.token, self.endpoint)
        payload = json.loads(response.text)  # convert json to dictionary
        features = payload["features"]  # get list of results
        first = (features[0])  # get first result
        properties = first["properties"]  # get properties of result (where address is)
        address = properties["address"]  # street address
        context = first["context"]  # get context (where zipcode and state are)
        postcode = [y for y in context if y["id"].startswith("postcode")][0]["text"] #zipcode
        region = [y for y in context if y["id"].startswith("region")][0]["text"] #state
        clean_address = dict()  # create dictionary for results
        clean_address["address"]=address
        clean_address["postcode"]=postcode
        clean_address["region"]=region
        return clean_address

def build_url(query, endpoint):
    """
    combine endpoint with query to call mapbox api
    :param query: unparsed address
    :param endpoint: mapbox api endpoint
    :return: url string
    """
    url = f"https://api.mapbox.com/{endpoint}/{requests.utils.quote(query)}.json"
    return url

def call_mapbox_endpoint(query, token, endpoint):
    """
    call mapbox api endpoint
    :param query: unparsed address
    :param token: api token
    :param endpoint: api endpoint
    :return: reponse form HTTP GET
    """
    url = build_url(query, endpoint)
    params = dict()

    params["access_token"]=token

    response = requests.get(url, params)
    return response

def get_token():
    """
    get api token from enviornment
    :return: api token
    """
    api_key = os.environ.get(ENV_VAR)
    if not api_key:
        raise PermissionError(f"API key missing in environment variable {ENV_VAR}")
        return None
    return api_key

if __name__=="__main__":
    token = get_token()
    response = call_mapbox_endpoint("the white house",token, GEOCODING_ENDPOINT_TEMPORARY)
    print(response.text)
