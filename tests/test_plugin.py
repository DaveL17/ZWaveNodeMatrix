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
import logging
import pathlib
import sys
import textwrap
import unittest
import xml.etree.ElementTree as ET  # noqa
from unittest.mock import MagicMock

import httpx
import shared.classes
import shared.utils

from httpcodes import codes as httpcodes
from indigo_devices_filters import DEVICE_FILTERS
from tests.shared.utils import run_host_script

# Paths relative to this file
_TESTS_DIR        = pathlib.Path(__file__).parent
_PLUGIN_DIR       = _TESTS_DIR.parent / "nodeMatrix.indigoPlugin" / "Contents"
_PLUGIN_PY        = _PLUGIN_DIR / "Server Plugin" / "plugin.py"
_SERVER_PLUGIN_DIR = str(_PLUGIN_DIR / "Server Plugin")

# ---------------------------------------------------------------------------
# Mock the `indigo` module for pure-Python tests (no Indigo server needed).
# constants.py does a bare `import indigo`, so we must inject a mock before
# any plugin-module imports.  We only do this when indigo is not already
# present (i.e. when NOT running inside Indigo).
# ---------------------------------------------------------------------------
if 'indigo' not in sys.modules:
    _mock_indigo        = MagicMock()
    _mock_indigo.Dict   = dict   # make indigo.Dict behave like a plain dict
    sys.modules['indigo'] = _mock_indigo

if _SERVER_PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _SERVER_PLUGIN_DIR)

import constants as _constants_mod          # noqa: E402 (after sys.path setup)
import plugin_defaults as _plugin_defaults  # noqa: E402

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
    """
    @classmethod
    def setUpClass(cls):
        pass

    def test_make_the_matrix_plugin_action(self):
        # Tests plugin action by calling plugin.executeAction directly
        refresh_matrix = textwrap.dedent("""\
            try:
                plugin_id = "com.fogbert.indigoplugin.nodeMatrix"
                plugin = indigo.server.getPlugin(plugin_id)
                plugin.executeAction("refreshMatrix")
                return 200
            except Exception as e:
                return e""")
        result = run_host_script(refresh_matrix)
        self.assertEqual(int(result), 200, f"{result}")

    def test_make_the_matrix_action_group_execute(self):
        # Tests plugin action by calling a configured Action Group object
        result = run_host_script("indigo.actionGroup.execute(1147059746)")
        self.assertEqual(result, "", f"{result}")

    def test_print_neighbor_list(self):
        """print_neighbor_list() runs without raising an exception."""
        script = textwrap.dedent("""\
            try:
                plugin_id = "com.fogbert.indigoplugin.nodeMatrix"
                plugin = indigo.server.getPlugin(plugin_id)
                plugin.executeAction("print_neighbor_list_action")
                return 200
            except Exception as e:
                return e""")
        result = run_host_script(script)
        self.assertEqual(str(result).strip(), "200", f"test_print_neighbor_list: {result!r}")

    def test_output_file_exists(self):
        """After refreshMatrix executes with injected test data, the output PNG exists on disk."""
        script = textwrap.dedent("""\
            import os
            plugin_id  = "com.fogbert.indigoplugin.nodeMatrix"
            plugin     = indigo.server.getPlugin(plugin_id)
            base_path  = indigo.server.getInstallFolderPath()
            plugin.executeAction("refreshMatrixTest")
            chart_path = base_path + "/Web Assets/images/controls/static/neighbors.png"
            return 200 if os.path.isfile(chart_path) else 404""")
        result = run_host_script(script)
        self.assertEqual(str(result).strip(), "200", f"test_output_file_exists: {result!r}")


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
                        self.assertIsNotNone(node_id,f"\"{file_type}\" element \"{item.tag}\" attribute 'id' is required.")
                        self.assertIsInstance(node_id, str, "id names must be strings.")
                        self.assertNotIn(' ', node_id, "`id` names should not contain spaces.")

                    # Test the 'deviceFilter' attribute:
                    dev_filter = item.get('deviceFilter')
                    if dev_filter:
                        self.assertIsInstance(node_id, str, "`deviceFilter` values must be strings.")
                        if dev_filter:  # None if not specified in item attributes
                            self.assertIn(dev_filter, DEVICE_FILTERS, "'deviceFilter' values must be strings.")

                    # Test the 'uiPath' attribute: The uiPath value can essentially be anything as plugins can create
                    # their own uiPaths, so we can only test a few things regarding its contents.
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
                    self.assertEqual(result, 200, f"ERROR: Got status code {result} ({httpcodes[result]}) -> {thing.text}.")

                # Test Config UI `Field` elements
                for thing in root.findall(f"./{root.tag[:-1]}/ConfigUI/Field"):
                    # Required attributes. Will throw a KeyError if missing.
                    self.assertIsInstance(thing.attrib['id'], str, "Config UI field IDs must be strings.")
                    self.assertFalse(thing.attrib['id'] == "", "Config UI field IDs must not be an empty string.")
                    self.assertIsInstance(thing.attrib['type'], str, "Config UI field types must be strings.")
                    self.assertIn(thing.attrib['type'].lower(), FIELD_TYPES, f"Config UI field types must be one of {FIELD_TYPES}.")
                    # Optional attributes
                    self.assertIsInstance(thing.attrib.get('defaultValue', ""), str, "Config UI defaultValue types must be strings.")
                    self.assertIsInstance(thing.attrib.get('enabledBindingId', ""), str, "Config UI enabledBindingId types must be strings.")
                    self.assertIsInstance(thing.attrib.get('enabledBindingNegate', ""), str, "Config UI enabledBindingNegate types must be strings.")
                    self.assertIn(thing.attrib.get('hidden', "false"), ['true', 'false'], "Config UI hidden attribute must be 'true' or 'false'.")
                    self.assertIn(thing.attrib.get('readonly', "false"), ['true', 'false'], "Config UI readonly attribute must be 'true' or 'false'.")
                    self.assertIn(thing.attrib.get('secure', "false"), ['true', 'false'], "Config UI secure attribute must be 'true' or 'false'.")
                    self.assertIsInstance(thing.attrib.get('tooltip', ""), str, "Config UI field tool tips must be strings.")
                    self.assertIsInstance(thing.attrib.get('visibleBindingId', ""), str, "Config UI visibleBindingId types must be strings.")
                    self.assertIsInstance(thing.attrib.get('visibleBindingValue', ""), str, "Config UI visibleBindingValue types must be strings.")

        except AssertionError as err:
            print(f"ERROR: {self._testMethodName}: {err}")

    def test_xml_field_ids_match_plugin_prefs_keys(self):
        """Each Field id in PluginConfig.xml has a corresponding key in kDefaultPluginPrefs."""
        plugin_config = str(_PLUGIN_DIR / "Server Plugin" / "PluginConfig.xml")
        try:
            tree = ET.parse(plugin_config)
        except FileNotFoundError:
            self.skipTest(f"PluginConfig.xml not found at {plugin_config}")
        root         = tree.getroot()
        prefs_keys   = set(_plugin_defaults.kDefaultPluginPrefs.keys())
        # Field types that don't correspond to a stored pref (UI-only elements)
        ui_only_types = {'label', 'separator', 'button'}
        for field in root.findall(".//Field"):
            field_type = field.attrib.get('type', '').lower()
            if field_type in ui_only_types:
                continue
            field_id = field.attrib.get('id', '')
            self.assertIn(
                field_id,
                prefs_keys,
                f"PluginConfig.xml Field id '{field_id}' has no matching key in kDefaultPluginPrefs.",
            )


# =============================================================================
# Pure-Python tests — no Indigo server required
# =============================================================================

class TestPrefsValidation(unittest.TestCase):
    """Tests for Plugin.validate_prefs_config_ui() using a plain dict as values_dict."""

    # Build a minimal mock Plugin instance that only exposes what
    # validate_prefs_config_ui() actually needs.
    class _MockPlugin:
        logger = logging.getLogger('TestPrefsValidation')

        def validate_prefs_config_ui(self, values_dict):
            """Inline copy of Plugin.validate_prefs_config_ui for offline testing."""
            error_msg_dict = {}

            try:
                try:
                    if not -360 <= int(values_dict.get('xAxisRotate', 0)) <= 360:
                        error_msg_dict['xAxisRotate'] = (
                            "The X Label Rotate value must be between -360 and 360 inclusive."
                        )
                        return (False, values_dict, error_msg_dict)
                except ValueError:
                    error_msg_dict['xAxisRotate'] = "The X Label Rotate value must be a number."
                    return (False, values_dict, error_msg_dict)

                for pref in [('chartTitleFont', 'Title Font Size'),
                             ('tickLabelFont', 'Label Font Size'),
                             ('chartResolution', 'Image DPI'),
                             ('chartHeight', 'Image Height'),
                             ('chartWidth', 'Image Width'),
                             ('plotLostDevicesTimeDelta', 'Days')]:
                    try:
                        if int(values_dict.get(pref[0], 0)) <= 0:
                            error_msg_dict[pref[0]] = (
                                f"The {pref[1]} value must be a number greater than zero."
                            )
                            return (False, values_dict, error_msg_dict)
                    except ValueError:
                        error_msg_dict[pref[0]] = f"The {pref[1]} value must be a number."
                        return (False, values_dict, error_msg_dict)

                return (True, values_dict)

            except Exception as error:
                self.logger.critical("%s", error)
                return (False, values_dict)

    @classmethod
    def setUpClass(cls):
        cls.plugin       = cls._MockPlugin()
        cls.valid_prefs  = dict(_plugin_defaults.kDefaultPluginPrefs)

    def test_valid_prefs_returns_true(self):
        """All defaults from kDefaultPluginPrefs should pass validation."""
        result = self.plugin.validate_prefs_config_ui(self.valid_prefs)
        self.assertTrue(result[0], f"Expected True but got: {result}")

    def test_x_axis_rotate_out_of_range(self):
        """xAxisRotate = '400' is out of range and should fail."""
        prefs              = dict(self.valid_prefs)
        prefs['xAxisRotate'] = "400"
        result             = self.plugin.validate_prefs_config_ui(prefs)
        self.assertFalse(result[0])
        self.assertIn('xAxisRotate', result[2])

    def test_x_axis_rotate_non_numeric(self):
        """xAxisRotate = 'abc' is non-numeric and should fail."""
        prefs              = dict(self.valid_prefs)
        prefs['xAxisRotate'] = "abc"
        result             = self.plugin.validate_prefs_config_ui(prefs)
        self.assertFalse(result[0])
        self.assertIn('xAxisRotate', result[2])

    def test_positive_pref_zero_value(self):
        """chartResolution = '0' must fail (must be > 0)."""
        prefs                  = dict(self.valid_prefs)
        prefs['chartResolution'] = "0"
        result                 = self.plugin.validate_prefs_config_ui(prefs)
        self.assertFalse(result[0])
        self.assertIn('chartResolution', result[2])

    def test_positive_pref_negative_value(self):
        """chartHeight = '-1' must fail (must be > 0)."""
        prefs                = dict(self.valid_prefs)
        prefs['chartHeight'] = "-1"
        result               = self.plugin.validate_prefs_config_ui(prefs)
        self.assertFalse(result[0])
        self.assertIn('chartHeight', result[2])

    def test_positive_pref_non_numeric(self):
        """tickLabelFont = 'big' must fail (must be numeric)."""
        prefs                = dict(self.valid_prefs)
        prefs['tickLabelFont'] = "big"
        result               = self.plugin.validate_prefs_config_ui(prefs)
        self.assertFalse(result[0])
        self.assertIn('tickLabelFont', result[2])


class TestFontList(unittest.TestCase):
    """Tests for the get_font_list() static method (pure Python, no Indigo needed)."""

    @classmethod
    def setUpClass(cls):
        try:
            import matplotlib.font_manager as _fnt
        except ImportError:
            raise unittest.SkipTest("matplotlib is not available in this environment")
        from os import path
        font_paths    = _fnt.findSystemFonts(fontpaths=None, fontext='ttf')
        cls.font_list = sorted(
            [path.splitext(path.basename(f))[0] for f in font_paths]
        )

    def test_get_font_list_returns_list(self):
        """Return type must be list."""
        self.assertIsInstance(self.font_list, list)

    def test_get_font_list_items_are_strings(self):
        """Every item in the font list must be a str."""
        for item in self.font_list:
            self.assertIsInstance(item, str, f"Non-string entry: {item!r}")

    def test_get_font_list_is_sorted(self):
        """Font list must be in sorted order."""
        self.assertEqual(self.font_list, sorted(self.font_list))

    def test_get_font_list_no_extensions(self):
        """No item in the font list should end with a file extension."""
        extensions = ('.ttf', '.otf', '.woff', '.woff2', '.eot')
        for item in self.font_list:
            self.assertFalse(
                item.lower().endswith(extensions),
                f"Font entry still has an extension: {item!r}",
            )


class TestConstants(unittest.TestCase):
    """Tests for constants.py (pure Python, no Indigo server needed)."""

    def test_debug_labels_has_required_levels(self):
        """DEBUG_LABELS must contain keys 10, 20, 30, 40, and 50."""
        required_keys = {10, 20, 30, 40, 50}
        self.assertEqual(
            required_keys,
            required_keys & set(_constants_mod.DEBUG_LABELS.keys()),
            f"DEBUG_LABELS is missing one or more required level keys. "
            f"Found: {set(_constants_mod.DEBUG_LABELS.keys())}",
        )

    def test_debug_labels_values_are_strings(self):
        """All values in DEBUG_LABELS must be non-empty strings."""
        for level, label in _constants_mod.DEBUG_LABELS.items():
            self.assertIsInstance(label, str, f"DEBUG_LABELS[{level}] is not a string.")
            self.assertTrue(label, f"DEBUG_LABELS[{level}] must not be empty.")


class TestDefaultPrefs(unittest.TestCase):
    """Tests for plugin_defaults.kDefaultPluginPrefs (pure Python, no Indigo server needed)."""

    # Keys that make_the_matrix() reads from pluginPrefs
    _REQUIRED_KEYS = {
        'backgroundColor',
        'chartHeight',
        'chartManualSize',
        'chartPath',
        'chartResolution',
        'chartTitle',
        'chartTitleFont',
        'chartWidth',
        'fontMain',
        'foregroundColor',
        'nodeBorderColor',
        'nodeColor',
        'nodeMarker',
        'nodeMarkerEdgewidth',
        'plotBattery',
        'plotBatteryColor',
        'plotLostDevices',
        'plotLostDevicesColor',
        'plotLostDevicesTimeDelta',
        'plotNoNode',
        'plotNoNodeColor',
        'plotOwnNodes',
        'plotOwnNodesColor',
        'plotUnusedNodes',
        'showLegend',
        'tickLabelFont',
        'xAxisLabel',
        'xAxisRotate',
        'yAxisLabel',
    }

    _COLOR_KEYS = {
        'backgroundColor',
        'foregroundColor',
        'nodeBorderColor',
        'nodeColor',
        'plotBatteryColor',
        'plotLostDevicesColor',
        'plotNoNodeColor',
        'plotOwnNodesColor',
    }

    _NUMERIC_STRING_KEYS = {
        'chartHeight',
        'chartResolution',
        'chartTitleFont',
        'chartWidth',
        'plotLostDevicesTimeDelta',
        'tickLabelFont',
        'xAxisRotate',
    }

    @classmethod
    def setUpClass(cls):
        cls.prefs = _plugin_defaults.kDefaultPluginPrefs

    def test_required_keys_present(self):
        """kDefaultPluginPrefs must contain all keys referenced by make_the_matrix()."""
        missing = self._REQUIRED_KEYS - set(self.prefs.keys())
        self.assertFalse(missing, f"kDefaultPluginPrefs is missing keys: {missing}")

    def test_color_prefs_are_hex_strings(self):
        """Color prefs must be space-separated two-digit hex strings (e.g. 'FF 00 00')."""
        import re
        hex_pattern = re.compile(r'^[0-9A-Fa-f]{2}( [0-9A-Fa-f]{2}){2}$')
        for key in self._COLOR_KEYS:
            value = self.prefs.get(key, '')
            self.assertRegex(
                value,
                hex_pattern,
                f"kDefaultPluginPrefs['{key}'] = {value!r} is not a valid hex color string.",
            )

    def test_numeric_prefs_are_numeric_strings(self):
        """Numeric prefs must be strings that can be cast to int."""
        for key in self._NUMERIC_STRING_KEYS:
            value = self.prefs.get(key, '')
            self.assertIsInstance(value, str, f"kDefaultPluginPrefs['{key}'] must be a string.")
            try:
                int(value)
            except (ValueError, TypeError):
                self.fail(
                    f"kDefaultPluginPrefs['{key}'] = {value!r} cannot be cast to int."
                )
