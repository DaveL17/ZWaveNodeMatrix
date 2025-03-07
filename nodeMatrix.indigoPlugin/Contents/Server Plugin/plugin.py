# noqa pylint: disable=too-many-lines, line-too-long, invalid-name, unused-argument, redefined-builtin, broad-except, fixme

"""
Z-Wave Node Matrix Indigo Plugin
author: DaveL17

Generates a graphical matrix of all Z-Wave devices and their neighbors. The plugin also provides some optional
supplemental information including missing devices (no communication for selected timeframe), highlights battery
devices (which may not be completely up-to-date), neighbors that no longer exist, and so on.
"""

# ================================== IMPORTS ==================================

# Built-in modules
import datetime
import logging
from os import path

# Third-party modules
import numpy as np  # noqa - included in Indigo Python 3 install
import matplotlib  # noqa - included in Indigo Python 3 install
# Note: this statement must be run before any other matplotlib imports are done.
matplotlib.use('AGG')
import matplotlib.font_manager as fnt  # noqa
import matplotlib.pyplot as plt  # noqa
try:
    import indigo  # noqa
except ImportError:
    pass

# My modules
import DLFramework.DLFramework as Dave
from constants import DEBUG_LABELS, INSTALL_PATH
from plugin_defaults import kDefaultPluginPrefs  # noqa

# =================================== HEADER ==================================
__author__    = Dave.__author__
__copyright__ = Dave.__copyright__
__license__   = Dave.__license__
__build__     = Dave.__build__
__title__     = 'Z-Wave Node Matrix Plugin'
__version__   = '2024.1.0'


# =============================================================================
class Plugin(indigo.PluginBase):
    """
    Standard Indigo Plugin Class

    :param indigo.PluginBase:
    """
    def __init__(self, plugin_id, plugin_display_name, plugin_version, plugin_prefs):
        """
        Plugin initialization

        :param str plugin_id:
        :param str plugin_display_name:
        :param str plugin_version:
        :param indigo.Dict plugin_prefs:
        """
        super().__init__(plugin_id, plugin_display_name, plugin_version, plugin_prefs)

        # ============================= Instance Variables =============================
        matplotlib.use('AGG')

        self.plugin_file_handler.setFormatter(logging.Formatter(Dave.LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S'))
        self.debug_level = int(self.pluginPrefs.get('showDebugLevel', '30'))
        self.indigo_log_handler.setLevel(self.debug_level)

        # ========================== Initialize DLFramework ===========================
        self.Fogbert = Dave.Fogbert(self)

        # =========================== Audit Server Version ============================
        self.Fogbert.audit_server_version(min_ver=2022)

    # =============================================================================
    def log_plugin_environment(self):
        """
        Log pluginEnvironment information when plugin is first started
        """
        self.Fogbert.pluginEnvironment()

    # =============================================================================
    # ============================== Indigo Methods ===============================
    # =============================================================================
    def validate_prefs_config_ui(self, values_dict):
        """
        Standard Indigo validation method called when plugin preferences dialog is closed.

        :param indigo.Dict values_dict:
        :return:
        """
        error_msg_dict = indigo.Dict()

        try:
            try:
                # `xAxisRotate` must be between -360 and 360. In essence, -360, 0, and 360 are all the same rotation.
                if not -360 <= int(values_dict.get('xAxisRotate', 0)) <= 360:
                    error_msg_dict['xAxisRotate'] = "The X Label Rotate value must be between -360 and 360 inclusive."
                    return False, values_dict, error_msg_dict
            except ValueError:
                error_msg_dict['xAxisRotate'] = "The X Label Rotate value must be a number."
                return False, values_dict, error_msg_dict

            # Preferences whose value must be a number greater than zero.
            for pref in [('chartTitleFont', 'Title Font Size'),
                         ('tickLabelFont', 'Label Font Size'),
                         ('chartResolution', 'Image DPI'),
                         ('chartHeight', 'Image Height'),
                         ('chartWidth', 'Image Width'),
                         ('plotLostDevicesTimeDelta', 'Days')
                         ]:
                try:
                    if not int(values_dict.get(pref[0], 0)) > 0:
                        error_msg_dict[pref[0]] = f"The {pref[1]} value must be a number greater than zero."
                        return False, values_dict, error_msg_dict
                except ValueError:
                    error_msg_dict[pref[0]] = f"The {pref[1]} value must be a number."
                    return False, values_dict, error_msg_dict

            return True, values_dict

        except Exception as error:
            self.logger.critical(f"{error}")

    # =============================================================================
    def closedPrefsConfigUi(self, values_dict: indigo.Dict = None, user_cancelled: bool = None) -> dict:  # noqa
        """
        Standard Indigo method called when plugin preferences dialog is closed.

        :param indigo.Dict values_dict:
        :param bool user_cancelled:
        :return:
        """
        if not user_cancelled:
            # Ensure that self.pluginPrefs includes any recent changes.
            for k in values_dict:
                self.pluginPrefs[k] = values_dict[k]

            # Debug Logging
            self.debug_level = int(values_dict.get('showDebugLevel', "30"))
            self.indigo_log_handler.setLevel(self.debug_level)
            indigo.server.log(f"Debugging on (Level: {DEBUG_LABELS[self.debug_level]} ({self.debug_level})")
            self.logger.debug("Plugin prefs saved.")

        else:
            self.logger.debug("Plugin prefs cancelled.")

        return values_dict

    # =============================================================================
    # ============================== Plugin Methods ===============================
    # =============================================================================
    @staticmethod
    def get_font_list(fltr: str = "", values_dict: indigo.Dict = None, type_id: int = 0, target_id: int = 0) -> list:  # noqa
        """
        Returns a list of available TrueType fonts

        Generates and returns a list of available fonts.  Note that these are the fonts that
        matplotlib can see, not necessarily all the fonts installed on the system.

        :param str fltr:
        :param indigo.Dict values_dict:
        :param str type_id:
        :param int target_id:
        :return:
        """
        font_list = fnt.findSystemFonts(fontpaths=None, fontext='ttf')
        names     = [path.splitext(path.basename(font))[0] for font in font_list]
        return sorted(names)

    # =============================================================================
    def make_the_matrix(self):
        """
        Generate the Z-Wave node matrix image

        General code to construct the Z-Wave node matrix image.

        :return:
        """
        bk_color               = self.pluginPrefs.get('backgroundColor', '00 00 00')
        background_color       = f"#{bk_color.replace(' ', '').replace('#', '')}"
        chart_title            = self.pluginPrefs.get('chartTitle', 'Z-Wave Node Matrix')
        chart_title_font       = int(self.pluginPrefs.get('chartTitleFont', 9))
        fnt_color              = self.pluginPrefs.get('foregroundColor', '88 88 88')
        font_color             = f"#{fnt_color.replace(' ', '').replace('#', '')}"
        font_name              = self.pluginPrefs.get('fontMain', 'Arial')
        fore_color             = self.pluginPrefs.get('foregroundColor', '88 88 88')
        foreground_color       = f"#{fore_color.replace(' ', '').replace('#', '')}"
        node_color             = f"#{self.pluginPrefs.get('nodeColor', 'FF FF FF').replace(' ', '')}"
        nd_clr_border          = self.pluginPrefs.get('nodeBorderColor', '66 FF 00')
        node_color_border      = f"#{nd_clr_border.replace(' ', '').replace('#', '')}"
        node_marker            = self.pluginPrefs.get('nodeMarker', '.')
        node_marker_edge_width = self.pluginPrefs.get('nodeMarkerEdgewidth', '1')
        file_path              = f"{INSTALL_PATH}Web Assets/images/controls/static/neighbors.png"
        output_file            = self.pluginPrefs.get('chartPath', file_path)
        tick_font_size         = int(self.pluginPrefs.get('tickLabelFont', 6))
        x_axis_label           = self.pluginPrefs.get('xAxisLabel', 'node')
        x_axis_rotate          = int(self.pluginPrefs.get('xAxisRotate', 0))
        y_axis_label           = self.pluginPrefs.get('yAxisLabel', 'neighbor')

        # If True, each node that is battery powered will be highlighted.
        plot_battery       = self.pluginPrefs.get('plotBattery', False)
        battery_color      = (self.pluginPrefs.get('plotBatteryColor', 'FF 00 00').replace(' ', '').replace('#', ''))
        plot_battery_color = f"#{battery_color}"

        # If True, neighbors without a corresponding node will be highlighted.
        plot_no_node       = self.pluginPrefs.get('plotNoNode', False)
        no_node_color      = (self.pluginPrefs.get('plotNoNodeColor', '00 33 FF').replace(' ', '').replace('#', ''))
        plot_no_node_color = f"#{no_node_color}"

        # If True, each node will be plotted as its own neighbor.
        plot_self       = self.pluginPrefs.get('plotOwnNodes', False)
        own_node_color  = (self.pluginPrefs.get('plotOwnNodesColor', '33 33 33').replace(' ', '').replace('#', ''))
        plot_self_color = f"#{own_node_color}"

        # If True, unused node addresses will be plotted.
        plot_unused_nodes = self.pluginPrefs.get('plotUnusedNodes', False)

        # If True, display a chart legend.
        show_legend = self.pluginPrefs.get('showLegend', False)

        # If True, the plugin settings will override chart sizing.
        override_chart_size = self.pluginPrefs.get('chartManualSize', False)

        # If True, the plugin will highlight devices that have not been updated in a user-specified
        # time (days.)
        plot_lost_devices  = self.pluginPrefs.get('plotLostDevices', False)
        update_delta       = int(self.pluginPrefs.get('plotLostDevicesTimeDelta', 7))
        lost_device        = self.pluginPrefs.get('plotLostDevicesColor', '66 00 CC').replace(' ', '').replace('#', '')
        lost_devices_color = f"#{lost_device}"

        # ================================== kwargs ===================================
        kwarg_savefig = {
            'bbox_extra_artists': None,
            'dpi': int(self.pluginPrefs.get('chartResolution', 100)),
            'edgecolor': background_color,
            'facecolor': background_color,
            'format': None,
            'orientation': None,
            'pad_inches': 0.1,
            'transparent': True
        }
        kwarg_title = {
            'color': font_color,
            'fontname': font_name,
            'fontsize': chart_title_font
        }

        if override_chart_size:
            chart_height = int(self.pluginPrefs.get('chartHeight', 7))
            chart_width  = int(self.pluginPrefs.get('chartWidth', 7))
            plt.figure(figsize=(chart_width, chart_height))

        # ========================== Build Master Dictionary ==========================
        # Build the master dictionary of the Z-Wave Mesh Network.
        counter       = 1
        device_dict   = {}
        neighbor_list = []

        # Iterate through all the Z-Wave devices and build a master dictionary.
        for dev in indigo.devices.iter('indigo.zwave'):
            dev_address = int(dev.address)
            neighbors   = (
                list(dev.ownerProps.get('zwNodeNeighbors', []))
            )

            # New device address
            if dev_address not in device_dict:
                device_dict[dev_address] = {}

                device_dict[dev_address]['battery'] = (
                    dev.ownerProps.get('SupportsBatteryLevel', False)
                )
                device_dict[dev_address]['changed']          = dev.lastChanged
                device_dict[dev_address]['invalid_neighbor'] = False
                device_dict[dev_address]['lost']             = False
                device_dict[dev_address]['neighbors']        = neighbors
                device_dict[dev_address]['no_node_1']        = False
                device_dict[dev_address]['name']             = dev.name

                counter += 1

            # Device address already in device_dict but device has neighbors (neighbor list not
            # empty)
            elif dev_address in device_dict and neighbors:
                device_dict[dev_address]['battery'] = (
                    dev.ownerProps.get('SupportsBatteryLevel', False)
                )
                device_dict[dev_address]['changed']   = dev.lastChanged
                device_dict[dev_address]['invalid_neighbor'] = False
                device_dict[dev_address]['lost']      = False
                device_dict[dev_address]['neighbors'] = neighbors
                device_dict[dev_address]['no_node_1'] = False
                device_dict[dev_address]['name']      = dev.name

            # Device address already in device_dict but device has no neighbors
            else:
                pass

        # Add a counter value to each device which is used to display a compressed X axis (show unused nodes = False)
        counter = 1
        for key in sorted(device_dict):
            device_dict[key]['counter'] = counter
            counter += 1

        # Dummy dict of devices for testing.
        # Note!!! the dummy dict won't work with the Print Neighbor List menu item because it queries the server and
        # not the dummy dict. Comment out before release.
        # from dummy_dict import test_file as device_dict  # pylint: disable=unused-wildcard-import  # TODO: comment this
        # self.logger.warning("Using dummy dict!!!")  # TODO: comment this

        dev_keys = list(device_dict)

        # If the dev_keys dict has zero len, there are no Z-Wave devices to plot.
        if len(dev_keys) < 1:
            self.logger.warning("No Z-Wave devices found.")
            return

        # ======================= Update Device Characteristics =======================
        for node in dev_keys:

            # No node 1 in neighbor list
            if 1 not in device_dict[node]['neighbors']:
                device_dict[node]['no_node_1'] = True

            # Device is lost
            device_delta = datetime.datetime.now() - device_dict[node]['changed']
            if device_delta > datetime.timedelta(days=update_delta):
                self.logger.warning(f"Lost Device - {node} [Node {device_dict[node]['name']}] {device_delta}")
                device_dict[node]['lost'] = True

            # Lists neighbor that is not an active address
            for neighbor in device_dict[node]['neighbors']:
                if neighbor not in dev_keys:
                    device_dict[node]['invalid_neighbor'] = True

            # ====================== Create a List of All Neighbors =======================
            # Add used nodes
            if node not in neighbor_list:
                neighbor_list.append(node)

            # Add known neighbors
            neighbor_list += [x for x in device_dict[node]['neighbors'] if x not in neighbor_list]
            neighbor_list = sorted(neighbor_list)

        dummy_y = {node: counter for counter, node in enumerate(neighbor_list, 1)}
        self.logger.debug(f"Device Dict: {device_dict}")

        # ============================= Lay Out The Plots =============================
        for node in dev_keys:

            # ================================= Plot Self =================================
            if plot_self:
                if plot_unused_nodes:
                    plt.plot(
                        node, node, marker=node_marker, markeredgewidth=node_marker_edge_width,
                        markeredgecolor=plot_self_color, markerfacecolor=node_color, zorder=11
                    )
                else:
                    plt.plot(
                        device_dict[node]['counter'], dummy_y[node], marker=node_marker,
                        markeredgewidth=node_marker_edge_width, markeredgecolor=plot_self_color,
                        markerfacecolor=node_color, zorder=11
                    )

            # ============================ Plot Neighbors =============================
            for neighbor in device_dict[node]['neighbors']:
                if plot_unused_nodes:
                    plt.plot(
                        node, neighbor, marker=node_marker, markeredgewidth=node_marker_edge_width,
                        markeredgecolor=node_color_border, markerfacecolor=node_color, zorder=9
                    )
                else:
                    plt.plot(
                        device_dict[node]['counter'], dummy_y[neighbor], marker=node_marker,
                        markeredgewidth=node_marker_edge_width, markeredgecolor=node_color_border,
                        markerfacecolor=node_color, zorder=9
                    )

                # =========================== Plot Battery Devices ============================
                if plot_battery:
                    if plot_unused_nodes and device_dict[node]['battery']:
                        plt.plot(
                            node, neighbor, marker=node_marker,
                            markeredgewidth=node_marker_edge_width,
                            markeredgecolor=plot_battery_color, markerfacecolor=node_color,
                            zorder=10
                        )
                    elif device_dict[node]['battery']:
                        plt.plot(
                            device_dict[node]['counter'], dummy_y[neighbor], marker=node_marker,
                            markeredgewidth=node_marker_edge_width,
                            markeredgecolor=plot_battery_color, markerfacecolor=node_color,
                            zorder=10
                        )

                # ============================= Plot Lost Devices =============================
                if plot_lost_devices and device_dict[node]['lost']:
                    if plot_unused_nodes:
                        plt.plot(
                            node, neighbor, marker=node_marker,
                            markeredgewidth=node_marker_edge_width,
                            markeredgecolor=lost_devices_color, markerfacecolor=node_color,
                            zorder=11
                        )
                    else:
                        plt.plot(
                            device_dict[node]['counter'], dummy_y[neighbor], marker=node_marker,
                            markeredgewidth=node_marker_edge_width,
                            markeredgecolor=lost_devices_color,
                            markerfacecolor=node_color, zorder=11
                        )

        # ============================== Chart Settings ===============================
        plt.title(chart_title, **kwarg_title)
        for spine in ('top', 'bottom', 'left', 'right'):
            plt.gca().spines[spine].set_color(foreground_color)
        plt.tick_params(axis='both', which='both', labelsize=tick_font_size, color=foreground_color)

        # ============================== X Axis Settings ==============================
        plt.xlabel(x_axis_label, fontname=font_name, fontsize=chart_title_font, color=foreground_color)
        plt.tick_params(axis='x', bottom=True, top=False)

        if plot_unused_nodes:
            plt.xticks(
                np.arange(1, max(dev_keys) + 1, 1), fontname=font_name, fontsize=tick_font_size,
                color=foreground_color, rotation=x_axis_rotate
            )
            plt.xlim(1, max(dev_keys) + 1)
        else:
            plt.xticks(
                np.arange(1, len(device_dict) + 1, 1), sorted(dev_keys), fontname=font_name,
                fontsize=tick_font_size, color=foreground_color, rotation=x_axis_rotate
            )
            plt.xlim(0, len(device_dict) + 1)

        # ============================== Y Axis Settings ==============================
        plt.ylabel(y_axis_label, fontname=font_name, fontsize=chart_title_font, color=foreground_color)
        plt.tick_params(axis='y', left=True, right=False)

        if plot_unused_nodes:
            plt.yticks(np.arange(1, max(dev_keys) + 1, 1), fontsize=tick_font_size, color=foreground_color)
            plt.ylim(0, max(dev_keys) + 1)
        else:
            plt.yticks(
                np.arange(1, len(list(dummy_y.keys())) + 1, 1), sorted(list(dummy_y.keys())),
                fontsize=tick_font_size, color=foreground_color
            )
            plt.ylim(0, len(dummy_y) + 1)

        # ============================== Legend Settings ==============================
        # Legend entries must be tuples.
        if show_legend:
            legend_labels = []
            legend_styles = []

            # Neighbor
            legend_labels.append("neighbor")
            legend_styles.append(
                tuple(plt.plot([], color=node_color_border, linestyle='', marker=node_marker,
                               markerfacecolor=node_color
                               )
                      )
            )

            if plot_battery:
                legend_labels.append("battery")
                legend_styles.append(
                    tuple(plt.plot([], color=plot_battery_color, linestyle='', marker=node_marker,
                                   markerfacecolor=node_color,
                                   markeredgewidth=node_marker_edge_width,
                                   markeredgecolor=plot_battery_color)
                          )
                )

            if plot_self:
                legend_labels.append("self")
                legend_styles.append(
                    tuple(plt.plot([], color=plot_self_color, linestyle='', marker=node_marker,
                                   markerfacecolor=node_color, markeredgecolor=plot_self_color)
                          )
                )

            if plot_lost_devices:
                legend_labels.append(f"lost ({update_delta})")
                legend_styles.append(
                    tuple(plt.plot([], color=lost_devices_color, linestyle='', marker=node_marker,
                                   markeredgewidth=node_marker_edge_width,
                                   markeredgecolor=lost_devices_color,
                                   markerfacecolor=node_color)
                          )
                )

            if plot_no_node:
                legend_labels.append("no node")
                legend_styles.append(
                    tuple(plt.plot([], color=plot_no_node_color, linestyle='', marker='x',
                                   markerfacecolor=plot_no_node_color)
                          )
                )

            legend = plt.legend(
                legend_styles, legend_labels, bbox_to_anchor=(1, 0.5), fancybox=True, loc='best',
                ncol=1, numpoints=1, prop={'family': font_name, 'size': 6.5}
            )
            legend.get_frame().set_alpha(0)
            _ = [text.set_color(font_color) for text in legend.get_texts()]

        # ================== Color labels for neighbors with no node ==================
        # Affects labels on the Y axis.
        if plot_no_node:
            y_tick_labels = list(plt.gca().get_yticklabels())

            for a in dummy_y:
                if a not in dev_keys:
                    if a != 1:
                        if plot_unused_nodes:
                            a -= 1
                            y_tick_labels[a].set_color(plot_no_node_color)

                        else:
                            a = dummy_y[a] - 1
                            y_tick_labels[a].set_color(plot_no_node_color)

        # ==================== Output the Z-Wave Node Matrix Image ====================
        try:
            plt.tight_layout()
            plt.savefig(output_file, **kwarg_savefig)
        except Exception:  # noqa
            self.logger.debug("Chart output error.", exc_info=True)
            self.logger.warning("Chart output error")

        # Wind things up.
        plt.close('all')
        self.logger.info("Z-Wave Node Matrix generated.")

    # =============================================================================
    def make_the_matrix_action(self, values_dict: indigo.Dict):  # noqa
        """
        Respond to menu call to generate a new image

        When the user calls for an updated image to be generated via the Refresh Matrix menu item,
        call self.make_the_matrix() method.

        :param indigo.Dict values_dict:
        :return:
        """
        self.make_the_matrix()


    # =============================================================================
    def print_neighbor_list(self):
        """
        Send a list of nodes/neighbors to the Indigo Events Log

        This method iterates all Z-Wave devices and logs their neighbor list.
        :return:
        """
        try:
            nodes_list = []

            # Iterate all Z-Wave Devices
            for dev in indigo.devices.iter(filter="indigo.zwave"):
                nodes = dev.ownerProps.get('zwNodeNeighborsStr', None)
                if nodes:
                    nodes_list.append(f"Node: {dev.address:<5}{nodes}")

            # Send the sorted list to the log
            indigo.server.log(f"========== Z-Wave Neighbors List ==========")
            sorted_nodes = sorted(nodes_list, key=lambda x: int(x.split()[1]))
            for node in sorted_nodes:
                indigo.server.log(f"{node}")  # Print the list regardless of debug logging setting
        except Exception as err:
            self.logger.warning(f"{err}")

    def my_tests(self, action: indigo.PluginAction = None) -> None:
        """
        The main unit test method

        The my_tests method is called from a plugin action item and, when called, imports all unit tests and runs them.
        If the unit test module returns True, then all tests have passed.
        """
        from Tests import test_plugin  # test_devices
        tests = test_plugin.TestPlugin()

        def process_test_result(result, name):
            if result[0] is True:
                self.logger.warning(f"{name} tests passed.")
            else:
                self.logger.warning(f"{result[1]}")

        # ===================================== Make Matrix =====================================
        test = tests.test_make_the_matrix(self)
        process_test_result(test, "Make Matrix")

        # ===================================== Execute Action =====================================
        test = tests.test_plugin_action(self)
        process_test_result(test, "Execute Action")

        # ===================================== Font List =====================================
        test = tests.test_get_font_list(self)
        process_test_result(test, "Font List")

        # ===================================== Prefs Validation =====================================
        test = tests.test_plugin_prefs_validation(self)
        process_test_result(test, "Prefs Validation")
