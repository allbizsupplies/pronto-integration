
import io
import os
from unittest import TestCase
from unittest.mock import mock_open, patch
import yaml

from common.settings import get_settings
from tests.fakes import fake_settings, random_string


class SettingsTest(TestCase):

    @patch("os.getcwd")
    def test_get_settings(self, mock_getcwd):
        type = random_string(10)
        filename = f"settings.{type}.yml"
        settings = fake_settings()
        with patch("builtins.open", mock_open(read_data=yaml.safe_dump(settings))) as mock_open_:
            result = get_settings(type)
            mock_open_.assert_called_with(os.path.join(
                mock_getcwd.return_value, filename))
            self.assertDictEqual(result, settings)
