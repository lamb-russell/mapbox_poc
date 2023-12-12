"""
call mapbox api
"""
import requests
import os
import json
import csv

ENV_VAR="MAPBOX_API_TOKEN"
GEOCODING_ENDPOINT_TEMPORARY = "geocoding/v5/mapbox.places"
GEOCODING_ENDPOINT_PERMANENT = "geocoding/v5/mapbox.places-permanent"


class MapboxGeocoder():
    """
    encapsulates api calling for MapBox geocoder api

    use get_clean_address to parse an address into its component parts.
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
        result = call_mapbox_endpoint(query, self.token, self.endpoint)
        clean_address = self.parse_request(result)
        return clean_address

    def parse_request(self, response_object, verbose=True):
        """
        parse address from response object
        :param response_object: http get response
        :param verbose: if true, include intermediate values in dictionary returned
        :return: dictionary with relevant values from response object
        """
        payload = json.loads(response_object.text)  # convert json to dictionary
        features = payload["features"]  # get list of results
        first = (features[0])  # get first result
        properties = first["properties"]  # get properties of result (where address is)

        result = dict()  # create dictionary for results
        result["address_property"] = properties.get("address")  # poi has street address in properties
        context = first["context"]  # context has more details about request in list form.  parse by id prefix
        # i use next() and iter() functions to get the first item in the list that matches the condition specified
        result["place_type"] = next(iter(first["place_type"]),None)  # place type from first feature
        result["address_feature"] = first.get("text") # street name
        result["street_number"] = first.get("address")  # street number
        result["postcode"] = next(iter([y["text"] for y in context if y["id"].startswith("postcode")]),None)  # zipcode
        result["region"] = next(iter([y["text"] for y in context if y["id"].startswith("region")]),None)  # state
        result["region_code"] = next(iter([y["short_code"] for y in context if y["id"].startswith("region")]), None)  # state code

        result["place"] = next(iter([y["text"] for y in context if y["id"].startswith("place")]), None)  # city

        result["locality"] = next(iter([y["text"] for y in context if y["id"].startswith("locality")]), None)  # state
        result["country"] = next(iter([y["text"] for y in context if y["id"].startswith("country")]), None)
        result["country_code"] = next(iter([y["short_code"] for y in context if y["id"].startswith("country")]), None)
        result["address"] = (result["address_property"] if result["place_type"]=="poi" # poi address has # and street
                             else f'{result["street_number"]} {result["address_feature"]}') # append number to street

        keys = [k for k in result] # need to store  keys separtely so we can modify dictionary
        if not verbose: # if not verbose, remove empty values from the dictionary
            for i in keys:
                if not result[i]: # remove keys from dictionary if value is None
                    result.pop(i)
        return result


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


def read_addresses_from_csv(file_path):
    """
    Read addresses from a CSV file.
    :param file_path: Path to the CSV file
    :return: List of addresses
    """
    # Expand the user's home directory symbol (~)
    expanded_path = os.path.expanduser(file_path)

    addresses = []
    with open(expanded_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header row if there is one
        for row in reader:
            addresses.append(row[0])  # Assuming address is in the first column
    return addresses

def save_results_to_csv(results, output_file):
    """
    Save the processed address data to a CSV file.
    :param results: List of dictionaries containing address data
    :param output_file: Path to the output CSV file
    """
    # Expand the user's home directory symbol (~)
    expanded_path = os.path.expanduser(output_file)

    with open(expanded_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        for result in results:
            try:
                writer.writerow(result)
            except Exception as ex:
                print(f"error writing result: {result}")
                print(ex)


if __name__=="__main__":
    #token = get_token()
    #response = call_mapbox_endpoint("the white house",token, GEOCODING_ENDPOINT_TEMPORARY)

    #print(response.text)

    #mbg=MapboxGeocoder()
    #parsed_address=mbg.get_clean_address("the white house")
    #print(parsed_address)

    input_csv = "~/Downloads/sweater_addresses.csv"  # Replace with your CSV file path
    output_csv = "~/Downloads/sweater_addresses_output.csv"  # Replace with your desired output file path

    addresses = read_addresses_from_csv(input_csv)

    geocoder = MapboxGeocoder()
    processed_addresses = []

    for address in addresses:
        try:
            clean_address = geocoder.get_clean_address(address)
            processed_addresses.append(clean_address)
            print(f"{address} - {clean_address}")
        except Exception as e:
            print(f"Error processing address '{address}': {e}")

    save_results_to_csv(processed_addresses, output_csv)
