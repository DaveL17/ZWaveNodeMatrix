"""
Unit tests for the Z-Wave Node Matrix plugin.

Menu Items are tested by referencing hidden Actions which have the same callback method.
"""
import dotenv
import httpx
import os
from tests.shared import APIBase # noqa

dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


# ===================================== simpleeval.py =====================================
class TestMenuItems(APIBase):

    @classmethod
    def setUpClass(cls):
        pass

    @staticmethod
    def _execute_action(action_id: str, msg: str = "test-plugin-menu-item") -> bool | httpx.Response:
        """Post a plugin.executeAction command to the Indigo Web Server API.

        Args:
            action_id (str): The Indigo action ID to execute.

        Returns:
            bool | httpx.Response: The HTTP response, or False if the request failed.
        """
        try:
            message = {
                "id": f"{msg}",
                "message": "plugin.executeAction",
                "pluginId": os.getenv("PLUGIN_ID"),
                "actionId": action_id,
            }
            url = f"{os.getenv('URL_PREFIX')}/v2/api/command/?api-key={os.getenv('GOOD_API_KEY')}"
            return httpx.post(url, json=message, verify=False)
        except Exception as e:
            print(f"API Error {e}")
            return False

    def test_refresh_matrix(self):
        """Post a plugin.refreshMatrix command to the Indigo Web Server."""
        result = self._execute_action("refreshMatrix", msg="test_refresh_matrix_action")
        self.assertEqual(result.status_code, 200, "The refresh matrix menu item call was not successful.")

    def test_print_neighbor_list(self):
        """Post a plugin.printNeighborList command to the Indigo Web Server."""
        result = self._execute_action("print_neighbor_list_action", msg="test_print_neighbor_list_action")
        self.assertEqual(result.status_code, 200, "The print neighbor list menu item call was not successful.")

    def test_print_environment_info(self):
        """Post a plugin.printEnvironmentInfo command to the Indigo Web Server."""
        result = self._execute_action("log_plugin_environment", msg="test_print_environment_info")
        self.assertEqual(result.status_code, 200, "The print environment info menu item call was not successful.")
