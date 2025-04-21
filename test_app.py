import unittest
from unittest.mock import patch
from background_sync_cache import fetch_cloud_data, get_cached_api_data
import json

class TestAppFunctions(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_cloud_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"metrics": "sample"}
        fetch_cloud_data()
        with open("athlete_data.json") as f:
            data = json.load(f)
        self.assertEqual(data["metrics"], "sample")

    @patch("requests.get")
    def test_get_cached_api_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"metrics": "sample"}
        data = get_cached_api_data()
        self.assertEqual(data["metrics"], "sample")

    @patch("requests.get")
    def test_get_cached_api_data_failure(self, mock_get):
        mock_get.return_value.status_code = 500
        data = get_cached_api_data()
        self.assertIsNone(data)

if __name__ == "__main__":
    unittest.main()
