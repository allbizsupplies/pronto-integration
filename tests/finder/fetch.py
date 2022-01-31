
import io
import json
from random import randint
import sys
from unittest import TestCase
from unittest.mock import patch

from finder.fetch import main
from tests.fakes import fake_order, fake_settings, random_string


class FetchTests(TestCase):

    @patch("finder.fetch.get_settings")
    @patch("finder.fetch.ODBCClient")
    def test_fetch_by_id(self, mock_client_class, mock_get_settings):
        """
        Fetches order by ID when query is an integer.
        """
        id = str(randint(10000, 99999))
        order = fake_order({
            "id": id,
        })
        settings = fake_settings()
        mock_get_settings.return_value = settings
        mock_client = mock_client_class.return_value
        mock_client.find_orders.return_value = [order]
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with patch.object(sys, "argv", ["", json.dumps({"query": id})]):
                main()
                mock_client_class.assert_called_with(settings)
                mock_client.find_orders.assert_called_with(id)
                output = mock_stdout.getvalue()
                result = json.loads(output)
                self.assertDictEqual(result, {
                    "orders": [order]
                })

    @patch("finder.fetch.get_settings")
    @patch("finder.fetch.ODBCClient")
    def test_fetch_by_id(self, mock_client_class, mock_get_settings):
        """
        Fetches orders by keywords when query is not an integer.
        """
        query = random_string(20)
        orders = [
            fake_order(),
            fake_order(),
        ]
        settings = fake_settings()
        mock_get_settings.return_value = settings
        mock_client = mock_client_class.return_value
        mock_client.find_orders.return_value = orders
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with patch.object(sys, "argv", ["", json.dumps({"query": query})]):
                main()
                mock_client_class.assert_called_with(settings)
                mock_client.find_orders.assert_called_with(query)
                output = mock_stdout.getvalue()
                result = json.loads(output)
                self.assertDictEqual(result, {
                    "orders": orders
                })

    @patch("finder.fetch.get_settings")
    @patch("finder.fetch.ODBCClient")
    def test_fetch_no_orders(self, mock_client_class, mock_get_settings):
        """
        Prints empty list of orders when order not found.
        """
        query = random_string(20)
        settings = fake_settings()
        mock_get_settings.return_value = settings
        mock_client = mock_client_class.return_value
        mock_client.find_orders.return_value = []
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with patch.object(sys, "argv", ["", json.dumps({"query": query})]):
                main()
                mock_client_class.assert_called_with(settings)
                mock_client.find_orders.assert_called_with(query)
                output = mock_stdout.getvalue()
                result = json.loads(output)
                self.assertDictEqual(result, {
                    "orders": []
                })
