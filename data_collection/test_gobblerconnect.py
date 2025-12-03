import unittest
from unittest.mock import patch, Mock, mock_open
import json

#import the functions to be tested
from gobblerconnect_organization_collection import (
    fetch_list_page,
    fetch_club_detail,
    extract_clean_club_data,
    scrape_all_clubs,
    BASE_SEARCH_URL,
    BASE_DETAIL_URL
)

class TestGobblerConnectScraper(unittest.TestCase):

    def test_extract_clean_club_data_full(self):
        """Test extracting data from a full detail dictionary."""
        detail = {
            "id": "12345",
            "name": "  Test Club  ",
            "shortName": "TC",
            "summary": "A club for testing.",
            "description": "<p>Description</p>",
            "categories": [{"id": "cat1", "name": "Category 1"}],
            "status": "Active",
            "visibility": "Public",
            "email": "test@example.com",
            "websiteKey": "testclub",
            "profilePicture": "image.jpg",
            "socialMedia": {"Facebook": "facebook.com/test"},
            "startDate": "2023-01-01T00:00:00Z",
            "modifiedOn": "2023-01-02T00:00:00Z",
            "primaryContact": {"name": "John Doe"},
            "extraField": "should be ignored"
        }
        expected = {
            "id": "12345",
            "name": "Test Club",
            "shortName": "TC",
            "summary": "A club for testing.",
            "description_html": "<p>Description</p>",
            "categories": [{"id": "cat1", "name": "Category 1"}],
            "status": "Active",
            "visibility": "Public",
            "email": "test@example.com",
            "websiteKey": "testclub",
            "profilePicture": "image.jpg",
            "socialMedia": {"Facebook": "facebook.com/test"},
            "startDate": "2023-01-01T00:00:00Z",
            "modifiedOn": "2023-01-02T00:00:00Z",
            "primaryContact": {"name": "John Doe"},
        }
        self.assertEqual(extract_clean_club_data(detail), expected)

    def test_extract_clean_club_data_minimal(self):
        """Test extracting data from a detail dictionary with missing optional fields."""
        detail = {
            "id": "54321",
            "name": "Minimal Club"
        }
        expected = {
            "id": "54321",
            "name": "Minimal Club",
            "shortName": None,
            "summary": None,
            "description_html": None,
            "categories": [],
            "status": None,
            "visibility": None,
            "email": None,
            "websiteKey": None,
            "profilePicture": None,
            "socialMedia": {},
            "startDate": None,
            "modifiedOn": None,
            "primaryContact": None,
        }
        self.assertEqual(extract_clean_club_data(detail), expected)

    def test_extract_clean_club_data_none(self):
        """Test handling of None input."""
        self.assertIsNone(extract_clean_club_data(None))

    @patch('gobblerconnect_organization_collection.requests.get')
    def test_fetch_list_page(self, mock_get):
        """Test fetching a page of organizations."""
        mock_response = Mock()
        expected_json = {"@odata.count": 1, "value": [{"Id": "123"}]}
        mock_response.json.return_value = expected_json
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_list_page(skip=0, top=1)

        mock_get.assert_called_once_with(BASE_SEARCH_URL, params={
            "orderBy[0]": "UpperName asc",
            "top": 1,
            "filter": "",
            "query": "",
            "skip": 0
        })
        self.assertEqual(result, expected_json)

    @patch('gobblerconnect_organization_collection.requests.get')
    def test_fetch_club_detail_success(self, mock_get):
        """Test fetching club details successfully."""
        club_id = "test-id"
        mock_response = Mock()
        expected_json = {"id": club_id, "name": "Test Club"}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        result = fetch_club_detail(club_id)

        expected_url = BASE_DETAIL_URL.format(club_id)
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_json)

    @patch('gobblerconnect_organization_collection.requests.get')
    def test_fetch_club_detail_failure(self, mock_get):
        """Test fetching club details with a non-200 status code."""
        club_id = "invalid-id"
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = fetch_club_detail(club_id)

        expected_url = BASE_DETAIL_URL.format(club_id)
        mock_get.assert_called_once_with(expected_url)
        self.assertIsNone(result)

    @patch('gobblerconnect_organization_collection.time.sleep')
    @patch('gobblerconnect_organization_collection.json.dump')
    @patch('gobblerconnect_organization_collection.open', new_callable=mock_open)
    @patch('gobblerconnect_organization_collection.fetch_club_detail')
    @patch('gobblerconnect_organization_collection.fetch_list_page')
    def test_scrape_all_clubs_integration(self, mock_fetch_list, mock_fetch_detail, mock_open_file, mock_json_dump, mock_sleep):
        """
        Integration test for the full scrape_all_clubs process.
        This test ensures that the functions for fetching, cleaning, and saving data
        work together as expected.
        """
        # mock setup
    
        mock_fetch_list.side_effect = [
            {"@odata.count": 2, "value": []},  # first call for total_count
            {"value": [{"Id": "club1"}, {"Id": "club2"}]}, # second call for the loop
        ]

        #called for each club ID found
        def detail_side_effect(club_id):
            if club_id == "club1":
                return {"id": "club1", "name": "Club One"}
            if club_id == "club2":
                return {"id": "club2", "name": "Club Two"}
            return None
        mock_fetch_detail.side_effect = detail_side_effect

        # call function
        scrape_all_clubs()

        # assertions
       
        self.assertEqual(mock_fetch_list.call_count, 2)

        #assert that details for each club were fetched
        mock_fetch_detail.assert_any_call("club1")
        mock_fetch_detail.assert_any_call("club2")
        self.assertEqual(mock_fetch_detail.call_count, 2)

        #assert that the file was opened for writing
        mock_open_file.assert_called_once_with("gobblerconnect_clubs.json", "w", encoding="utf-8")

        #assert that json.dump was called with the correct data
        expected_data = {
            "club1": extract_clean_club_data({"id": "club1", "name": "Club One"}),
            "club2": extract_clean_club_data({"id": "club2", "name": "Club Two"})
        }
        mock_json_dump.assert_called_once_with(expected_data, mock_open_file(), indent=4)

if __name__ == '__main__':
    unittest.main()