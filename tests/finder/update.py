
import io
import json
from random import randint
import sys
from unittest import TestCase
from unittest.mock import patch

from finder.update import main
from tests.fakes import fake_order, fake_settings, random_string


class UpdateTests(TestCase):

    @patch("finder.update.get_settings")
    @patch("finder.update.ODBCClient")
    def test_update(self, mock_client_class, mock_get_settings):
        """
        Updates order by ID when query is an integer.
        """
        order = fake_order({
            "location": random_string(20),
        })
        data = {
            "id": order["id"],
            "values": {
                "location": order["location"],
            }
        }
        settings = fake_settings()
        mock_get_settings.return_value = settings
        mock_client = mock_client_class.return_value
        mock_client.update_order.return_value = order
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with patch.object(sys, "argv", ["", json.dumps(data)]):
                main()
                mock_client_class.assert_called_with(settings)
                mock_client.update_order.assert_called_with(
                    data["id"], data["values"])
                output = mock_stdout.getvalue()
                result = json.loads(output)
                self.assertDictEqual(result, {
                    "order": order,
                })
