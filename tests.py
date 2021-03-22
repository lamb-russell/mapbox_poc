import unittest
import json
from main import call_mapbox_endpoint, get_token, GEOCODING_ENDPOINT_TEMPORARY, MapboxGeocoder
class TestGeocoding(unittest.TestCase):
    def test_call_endpoint(self):
        token = get_token()
        response = call_mapbox_endpoint("the white house",token,GEOCODING_ENDPOINT_TEMPORARY )

        payload = json.loads(response.text) #convert json to dictionary
        features=payload["features"] # get list of results
        first=(features[0]) # get first result
        properties = first["properties"] # get properties of result (where address is)
        address = properties["address"] # street address
        self.assertEqual(address,'1600 Pennsylvania Ave NW')
        context = first["context"] # get context (where zipcode and state are)

        postcode = [y for y in context if y["id"].startswith("postcode")][0]["text"]
        region = [y for y in context if y["id"].startswith("region")][0]["text"]
        self.assertEqual(postcode,"20006")
        self.assertEqual(region,"District of Columbia")


    def test_geocoder_class(self):
        mg = MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
        response = mg.geocode("the white house")
        payload = json.loads(response.text)
        address = payload["features"][0]["properties"]["address"]
        self.assertEqual(address, '1600 Pennsylvania Ave NW')

    def test_clean_address(self):
        mg = MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
        result = mg.get_clean_address("the white house")

        self.assertEqual(result["address"], '1600 Pennsylvania Ave NW')
        self.assertEqual(result["postcode"], "20006")
        self.assertEqual(result["region"], "District of Columbia")