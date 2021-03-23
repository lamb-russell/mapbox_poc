import unittest
import json
from mapbox import call_mapbox_endpoint, get_token, GEOCODING_ENDPOINT_TEMPORARY, MapboxGeocoder
class TestMapboxGeocoding(unittest.TestCase):
    def test_call_endpoint(self):
        """
        test api call using point of interest
        :return:
        """
        token = get_token()
        response = call_mapbox_endpoint("the white house",token,GEOCODING_ENDPOINT_TEMPORARY )

        payload = json.loads(response.text) #convert json to dictionary
        features=payload["features"] # get list of results
        first=(features[0]) # get first result
        properties = first["properties"] # get properties of result (where address is)
        address = properties["address"] # street address
        self.assertEqual(address,'1600 Pennsylvania Ave NW')
        context = first["context"] # get context (where zipcode and state are)
        print(first)
        postcode = [y for y in context if y["id"].startswith("postcode")][0]["text"]
        region = [y for y in context if y["id"].startswith("region")][0]["text"]
        self.assertEqual(postcode,"20006")
        self.assertEqual(region,"District of Columbia")


    def test_geocoder_class(self):
        """
        check geocoder using point of interest
        :return:
        """
        mg = MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
        response = mg.geocode("the white house")
        payload = json.loads(response.text)
        address = payload["features"][0]["properties"]["address"]
        self.assertEqual(address, '1600 Pennsylvania Ave NW')

    def test_clean_address(self):
        """
        check get clean address function using Point of interest
        :return:
        """
        mg = MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
        result = mg.get_clean_address("the white house")
        self.assertEqual(result["address"], '1600 Pennsylvania Ave NW')
        self.assertEqual(result["postcode"], "20006")
        self.assertEqual(result["region"], "District of Columbia")

    def test_parse_request(self):
        """
        check results from parse request function using an address
        :return:
        """
        mg=MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
        response = mg.geocode("21 flushing ave 11205 new york")
        result=mg.parse_request(response)
        self.assertEqual(result["address"],"21 Flushing Avenue")
        self.assertEqual(result["locality"],"Brooklyn")
        self.assertEqual(result["postcode"], "11205")
        self.assertEqual(result["region"], "New York")

        #print(features[0]["properties"])
