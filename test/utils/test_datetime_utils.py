import unittest
from utils import datetime_utils


class TestDateTimeUtils(unittest.TestCase):

    def test_parse_start_datetime_valid_date(self):
        # Given
        date_str = '2021-06-24T14:33:00Z'

        # When
        result = datetime_utils.parse_start_datetime(date_str)

        # Then
        self.assertEqual(result.year, 2021)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 24)
        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 33)

    def test_parse_start_datetime_invalid_date_str(self):
        # Given
        date_str = '2021-13-24T14:33:00Z'

        # When
        result = datetime_utils.parse_start_datetime(date_str)

        # Then
        self.assertIsNone(result)

    def test_parse_start_datetime_invalid_date_input_type(self):
        # Given
        date_str = 12

        # When
        result = datetime_utils.parse_start_datetime(date_str)

        # Then
        self.assertIsNone(result)
