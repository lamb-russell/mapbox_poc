import unittest
import json
import requests
import os
import tempfile
from mapbox import call_mapbox_endpoint, get_token, GEOCODING_ENDPOINT_TEMPORARY, MapboxGeocoder, build_url, read_addresses_from_csv, save_results_to_csv
from unittest.mock import patch, Mock

class TestMapboxGeocoderInitialization(unittest.TestCase):

    def test_default_initialization(self):
        geocoder = MapboxGeocoder()
        self.assertEqual(geocoder.endpoint, GEOCODING_ENDPOINT_TEMPORARY)

    def test_custom_endpoint_initialization(self):
        custom_endpoint = "custom/endpoint"
        geocoder = MapboxGeocoder(endpoint=custom_endpoint)
        self.assertEqual(geocoder.endpoint, custom_endpoint)



class TestGeocodeMethod(unittest.TestCase):

    @patch('mapbox.call_mapbox_endpoint')
    def test_geocode(self, mock_call_mapbox_endpoint):
        mock_response = Mock()
        mock_call_mapbox_endpoint.return_value = mock_response
        geocoder = MapboxGeocoder()
        response = geocoder.geocode("test query")
        self.assertEqual(response, mock_response)

class TestGetCleanAddressMethod(unittest.TestCase):

    @patch('mapbox.call_mapbox_endpoint')
    def test_get_clean_address(self, mock_call_mapbox_endpoint):
        mock_response = Mock()
        mock_response.text = '{"features": [{"properties": {"address": "123"}, "context": [], "place_type": ["poi"], "text": "Main St", "address": "123"}]}'
        mock_call_mapbox_endpoint.return_value = mock_response

        geocoder = MapboxGeocoder()
        result = geocoder.get_clean_address("test query")
        self.assertIn("address_property", result)

class TestBuildUrlFunction(unittest.TestCase):

    def test_build_url(self):
        query = "123 Main St"
        endpoint = "test/endpoint"
        expected_url = f"https://api.mapbox.com/{endpoint}/{requests.utils.quote(query)}.json"
        self.assertEqual(build_url(query, endpoint), expected_url)

class TestReadAddressesFromCsv(unittest.TestCase):

    def test_read_addresses_from_csv(self):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp.write("Address\n123 Main St\n456 Elm St")
            tmp_path = tmp.name

        try:
            addresses = read_addresses_from_csv(tmp_path)
            self.assertEqual(addresses, ["123 Main St", "456 Elm St"])
        finally:
            os.remove(tmp_path)


class TestSaveResultsToCsv(unittest.TestCase):

    def test_save_results_to_csv(self):
        results = [{"address": "123 Main St"}, {"address": "456 Elm St"}]
        with tempfile.NamedTemporaryFile(mode='r+', delete=False) as tmp:
            save_results_to_csv(results, tmp.name)
            tmp.seek(0)
            content = tmp.read()
            self.assertIn("123 Main St", content)
            self.assertIn("456 Elm St", content)


class TestCallMapboxEndpoint(unittest.TestCase):

    @patch('requests.get')
    def test_call_mapbox_endpoint(self, mock_get):
        mock_response = Mock()
        mock_get.return_value = mock_response
        response = call_mapbox_endpoint("test query", "test_token", "test/endpoint")
        self.assertEqual(response, mock_response)


class TestMapboxGeocoding(unittest.TestCase):
    # def test_call_endpoint(self):
    #     """
    #     test api call using point of interest
    #     :return:
    #     """
    #     token = get_token()
    #     response = call_mapbox_endpoint("the white house",token,GEOCODING_ENDPOINT_TEMPORARY )
    #
    #     payload = json.loads(response.text) #convert json to dictionary
    #     features=payload["features"] # get list of results
    #     first=(features[0]) # get first result
    #     properties = first["properties"] # get properties of result (where address is)
    #     address = properties["address"] # street address
    #     self.assertEqual(address,'1600 Pennsylvania Ave NW')
    #     context = first["context"] # get context (where zipcode and state are)
    #     print(first)
    #     postcode = [y for y in context if y["id"].startswith("postcode")][0]["text"]
    #     region = [y for y in context if y["id"].startswith("region")][0]["text"]
    #     self.assertEqual(postcode,"20006")
    #     self.assertEqual(region,"District of Columbia")


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


    # def test_clean_address(self):
    #     """
    #     check get clean address function using Point of interest
    #     :return:
    #     """
    #     mg = MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
    #     result = mg.get_clean_address("the white house")
    #     self.assertEqual(result["address"], '1600 Pennsylvania Ave NW')
    #     self.assertEqual(result["postcode"], "20006")
    #     self.assertEqual(result["region"], "District of Columbia")

    def test_parse_request(self):
        """
        check results from parse request function using an address
        :return:
        """
        mg=MapboxGeocoder(GEOCODING_ENDPOINT_TEMPORARY)
        response = mg.geocode("21 flushing ave 11205 new york")
        #print(response.text)
        result=mg.parse_request(response)
        self.assertEqual(result["address"],"21 Flushing Avenue")
        self.assertEqual(result["locality"],"Brooklyn")
        self.assertEqual(result["postcode"], "11205")
        self.assertEqual(result["region"], "New York")
        print(result)
        #print(features[0]["properties"])

if __name__ == '__main__':
    unittest.main()

