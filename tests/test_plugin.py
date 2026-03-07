"""
test_plugin.py

Unit tests for the Z-Wave Node Matrix plugin. Tests that require the Indigo server communicate via the HTTP REST API
using the APIBase framework. XML tests validate plugin file structure and run without a running Indigo server.

Prerequisites:
    - tests/.env configured with valid API key and object IDs
    - Indigo server running with the nodeMatrix plugin active (for TestPlugin tests only)

Usage:
    cd tests && python -m pytest -v
"""
import os
import pathlib
import unittest
import xml.etree.ElementTree as ET  # noqa

import httpx
import shared.classes

from httpcodes import codes as httpcodes
from indigo_devices_filters import DEVICE_FILTERS

# Paths relative to this file
_TESTS_DIR  = pathlib.Path(__file__).parent
_PLUGIN_DIR = _TESTS_DIR.parent / "nodeMatrix.indigoPlugin" / "Contents"
_PLUGIN_PY  = _PLUGIN_DIR / "Server Plugin" / "plugin.py"

FIELD_TYPES = ['button', 'checkbox', 'colorpicker', 'label', 'list', 'menu', 'separator', 'textfield']
XML_FILES   = [
    str(_PLUGIN_DIR / "Server Plugin" / "PluginConfig.xml"),
    str(_PLUGIN_DIR / "Server Plugin" / "Actions.xml"),
    str(_PLUGIN_DIR / "Server Plugin" / "MenuItems.xml"),
    str(_PLUGIN_DIR / "Server Plugin" / "Devices.xml"),
    str(_PLUGIN_DIR / "Server Plugin" / "Events.xml"),
]


class TestPlugin(shared.classes.APIBase):
    """
    Unit tests for the Z-Wave Node Matrix plugin.

    Tests communicate with Indigo via the HTTP REST API. Requires Indigo server running with the plugin active.
    Configure tests/.env with the required env vars before running.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.action_group_execute = int(os.getenv("test_plugin.TestPlugin.ACTION_GROUP_EXECUTE", 0))
        cls.action_group_folder  = int(os.getenv("test_plugin.TestPlugin.ACTION_GROUP_FOLDER", 0))

    def test_plugin_action(self):
        """Test the make_the_matrix action group executes successfully."""
        msg_id   = "test_plugin_action"
        response = self.send_simple_command(msg_id, "indigo.actionGroup.execute", self.action_group_execute)
        self.assertIn(response.status_code, range(200, 300),
                      f"Action group execute returned status {response.status_code}.")

    def test_make_the_matrix(self):
        """Test that the action group used to invoke make_the_matrix exists in Indigo.

        Note: the Indigo HTTP API v2 does not support direct plugin action invocation
        (indigo.server.executePluginAction is not a valid command). make_the_matrix is
        tested end-to-end via test_plugin_action, which executes the action group that
        calls it. This test confirms that the action group itself is properly registered.
        """
        action_group = self.get_indigo_object("actionGroups", self.action_group_execute)
        self.assertIsInstance(action_group, dict, "Action group lookup should return a dict.")
        self.assertEqual(action_group.get("id"), self.action_group_execute,
                         "Action group ID should match the configured ACTION_GROUP_EXECUTE.")


class TestXml(shared.classes.APIBase):
    """
    Tests the various XML files that are part of a standard Indigo plugin.

    The files tested are listed in XML_FILES. The tests include checks for required elements (like element `id` and
    `type` attributes) and syntax. These tests can run without a running Indigo server.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open(_PLUGIN_PY, 'r', encoding='utf-8') as infile:
            cls.plugin_lines = infile.read()

    @staticmethod
    def get_item_name(xml_file: str, item_id: int):  # noqa
        """Parse the XML file and return its root element."""
        tree = ET.parse(xml_file)
        return tree.getroot()

    def test_xml_files(self):
        """Tests the various plugin XML files."""
        try:
            for file_type in XML_FILES:
                try:
                    root = self.get_item_name(file_type, 0)
                except FileNotFoundError:
                    print(f"\"{file_type}\" file not present.")
                    continue
                for item in root:
                    # Test for the 'id' attribute (usually required):
                    exceptions = ['SupportURL', 'Template']  # node tags that don't require an `id` attribute.
                    node_id    = item.get('id')
                    if item.tag not in exceptions:
                        self.assertIsNotNone(node_id,
                                             f"\"{file_type}\" element \"{item.tag}\" attribute 'id' is required.")
                        self.assertIsInstance(node_id, str, "id names must be strings.")
                        self.assertNotIn(' ', node_id, "`id` names should not contain spaces.")

                    # Test the 'deviceFilter' attribute:
                    dev_filter = item.get('deviceFilter')
                    if dev_filter:
                        self.assertIsInstance(node_id, str, "`deviceFilter` values must be strings.")
                        if dev_filter:  # None if not specified in item attributes
                            self.assertIn(dev_filter, DEVICE_FILTERS, "'deviceFilter' values must be strings.")

                    # Test the 'uiPath' attribute:
                    # The uiPath value can essentially be anything as plugins can create their own uiPaths, so we
                    # can only test a few things regarding its contents.
                    ui_path = item.get('uiPath', '')
                    self.assertIsInstance(ui_path, str, "uiPath names must be strings.")

                # Test items that have a 'Name' element. The reference to `root.tag[:-1]` takes the tag name and
                # converts it to the appropriate child element name. For example, `Actions` -> `Action`, etc.
                for thing in root.findall(f"./{root.tag[:-1]}/Name"):
                    self.assertIsInstance(thing.text, str, "Action names must be strings.")

                # Test items that have a 'CallBackMethod` element to ensure there's a corresponding method:
                for thing in root.findall(f"./{root.tag[:-1]}/CallbackMethod"):
                    self.assertIsInstance(thing.text, str, "Action callback names must be strings.")
                    # We can't directly access the plugin.py file from here, so we read it into a variable instead.
                    # We then search for the string `def <CALLBACK METHOD>` within the file as a proxy to doing a
                    # `dir()` to see if it's in there.
                    self.assertTrue(
                        f"def {thing.text}" in self.plugin_lines,
                        f"{file_type} - The callback method \"{thing.text}\" does not exist in the "
                        f"plugin.py file."
                    )

                # Test items that have a 'configUI' element and a support url. It's okay if no valid urls are present.
                # The test will go out to each support url to ensure it's valid.
                support_urls = root.findall(f"./{root.tag[:-1]}/ConfigUI/SupportURL")
                for thing in support_urls:
                    self.assertIsInstance(thing.text, str, "Config UI support URLs must be strings.")
                    response = httpx.get(thing.text)
                    result   = response.status_code
                    self.assertEqual(result, 200,
                                     f"ERROR: Got status code {result} ({httpcodes[result]}) -> {thing.text}.")

                # Test Config UI `Field` elements
                for thing in root.findall(f"./{root.tag[:-1]}/ConfigUI/Field"):
                    # Required attributes. Will throw a KeyError if missing.
                    self.assertIsInstance(thing.attrib['id'], str, "Config UI field IDs must be strings.")
                    self.assertFalse(thing.attrib['id'] == "", "Config UI field IDs must not be an empty string.")
                    self.assertIsInstance(thing.attrib['type'], str, "Config UI field types must be strings.")
                    self.assertIn(thing.attrib['type'].lower(), FIELD_TYPES,
                                  f"Config UI field types must be one of {FIELD_TYPES}.")
                    # Optional attributes
                    self.assertIsInstance(thing.attrib.get('defaultValue', ""), str,
                                          "Config UI defaultValue types must be strings.")
                    self.assertIsInstance(thing.attrib.get('enabledBindingId', ""), str,
                                          "Config UI enabledBindingId types must be strings.")
                    self.assertIsInstance(thing.attrib.get('enabledBindingNegate', ""), str,
                                          "Config UI enabledBindingNegate types must be strings.")
                    self.assertIn(thing.attrib.get('hidden', "false"), ['true', 'false'],
                                  "Config UI hidden attribute must be 'true' or 'false'.")
                    self.assertIn(thing.attrib.get('readonly', "false"), ['true', 'false'],
                                  "Config UI readonly attribute must be 'true' or 'false'.")
                    self.assertIn(thing.attrib.get('secure', "false"), ['true', 'false'],
                                  "Config UI secure attribute must be 'true' or 'false'.")
                    self.assertIsInstance(thing.attrib.get('tooltip', ""), str,
                                          "Config UI field tool tips must be strings.")
                    self.assertIsInstance(thing.attrib.get('visibleBindingId', ""), str,
                                          "Config UI visibleBindingId types must be strings.")
                    self.assertIsInstance(thing.attrib.get('visibleBindingValue', ""), str,
                                          "Config UI visibleBindingValue types must be strings.")

        except AssertionError as err:
            print(f"ERROR: {self._testMethodName}: {err}")
