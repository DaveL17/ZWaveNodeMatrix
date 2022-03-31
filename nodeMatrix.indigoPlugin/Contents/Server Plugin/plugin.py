# noqa pylint: disable=too-many-lines, line-too-long, invalid-name, unused-argument, redefined-builtin, broad-except, fixme

"""
Z-Wave Node Matrix Indigo Plugin
author: DaveL17

Generates a graphical matrix of all Z-Wave devices and their neighbors. The plugin also provides
some optional supplemental information including missing devices (no communication for selected
timeframe), highlights battery devices (which may not be completely up-to-date), neighbors that no
longer exist, and so on.
"""
# =================================== TO DO ===================================
# TODO: None

# ================================== IMPORTS ==================================

# Built-in modules
import datetime
import logging
from os import path

# Third-party modules
import matplotlib
# Note: this statement must be run before any other matplotlib imports are done.
matplotlib.use('AGG')
import matplotlib.font_manager as fnt
import matplotlib.pyplot as plt
import numpy as np
try:
    import indigo  # noqa
except ImportError:
    pass
# try:
#     import pydevd
# except ImportError:
#     pass

# My modules
import DLFramework.DLFramework as Dave
from constants import *  # noqa, pylint: disable=unused-wildcard-import
from plugin_defaults import kDefaultPluginPrefs  # noqa

# =================================== HEADER ==================================
__author__    = Dave.__author__
__copyright__ = Dave.__copyright__
__license__   = Dave.__license__
__build__     = Dave.__build__
__title__     = 'Z-Wave Node Matrix Plugin'
__version__   = '2022.0.1'


# =============================================================================
class Plugin(indigo.PluginBase):
    """
    Title Placeholder

    Body placeholder
    """
    def __init__(self, plugin_id, plugin_display_name, plugin_version, plugin_prefs):
        """
        Title Placeholder

        Body placeholder

        :param str plugin_id:
        :param str plugin_display_name:
        :param str plugin_version:
        :param indigo.Dict plugin_prefs:
        :return:
        """
        super().__init__(plugin_id, plugin_display_name, plugin_version, plugin_prefs)

        # ============================= Instance Variables =============================
        self.pluginIsInitializing = True
        self.pluginIsShuttingDown = False
        matplotlib.use('AGG')

        log_format = '%(asctime)s.%(msecs)03d\t%(levelname)-10s\t%(name)s.%(funcName)-28s %(msg)s'
        self.debugLevel = int(self.pluginPrefs.get('showDebugLevel', '30'))
        self.plugin_file_handler.setFormatter(
            logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
        )
        self.indigo_log_handler.setLevel(self.debugLevel)

        # ========================== Initialize DLFramework ===========================
        self.Fogbert = Dave.Fogbert(self)
        # Log pluginEnvironment information when plugin is first started
        self.Fogbert.pluginEnvironment()

        # ============================= Remote Debugging ==============================
        # try:
        #     pydevd.settrace(
        #         'localhost',
        #         port=5678,
        #         stdoutToServer=True,
        #         stderrToServer=True,
        #         suspend=False
        #     )
        # except:
        #     pass

        self.pluginIsInitializing = False

    # =============================================================================
    def __del__(self):
        """
        Title Placeholder

        Body placeholder

        :return:
        """
        indigo.PluginBase.__del__(self)

    # =============================================================================
    # ============================== Indigo Methods ===============================
    # =============================================================================
    def closedPrefsConfigUi(self, values_dict, user_cancelled):  # noqa
        """
        Title Placeholder

        Body placeholder

        :param indigo.Dict values_dict:
        :param bool user_cancelled:
        :return:
        """
        if not user_cancelled:

            # Ensure that self.pluginPrefs includes any recent changes.
            for k in values_dict:
                self.pluginPrefs[k] = values_dict[k]

            self.debugLevel = int(values_dict['showDebugLevel'])
            self.indigo_log_handler.setLevel(self.debugLevel)

            self.logger.debug("User prefs saved.")

        else:
            self.logger.debug("User prefs cancelled.")

    # =============================================================================
    @staticmethod
    def sendDevicePing(dev_id=0, suppress_logging=False):  # noqa
        """
        Title Placeholder

        Body placeholder

        :param int dev_id:
        :param bool suppress_logging:
        :return:
        """
        indigo.server.log("ZWaveNodeMatrix Plugin devices do not support the ping function.")
        return {'result': 'Failure'}

    # =============================================================================
    def startup(self):
        """
        Title Placeholder

        Body placeholder

        :return:
        """
        # =========================== Audit Server Version ============================
        self.Fogbert.audit_server_version(min_ver=2022)

    # =============================================================================
    def stopConcurrentThread(self):  # noqa
        """
        Title Placeholder

        Body placeholder

        :return:
        """
        self.pluginIsShuttingDown = True

    # =============================================================================
    # ============================== Plugin Methods ===============================
    # =============================================================================
    @staticmethod
    def get_font_list(fltr="", type_id=0, values_dict=None, target_id=0):  # noqa
        """
        Returns a list of available TrueType fonts

        Generates and returns a list of available fonts.  Note that these are the fonts that
        matplotlib can see, not necessarily all the fonts installed on the system.

        :param str fltr:
        :param str type_id:
        :param indigo.Dict values_dict:
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
        bk_color = self.pluginPrefs.get('backgroundColor', '00 00 00')
        background_color = f"#{bk_color.replace(' ', '').replace('#', '')}"
        chart_title = self.pluginPrefs.get('chartTitle', 'Z-Wave Node Matrix')
        chart_title_font = int(self.pluginPrefs.get('chartTitleFont', 9))
        fnt_color = self.pluginPrefs.get('foregroundColor', '88 88 88')
        font_color = f"#{fnt_color.replace(' ', '').replace('#', '')}"
        font_name = self.pluginPrefs.get('fontMain', 'Arial')
        fore_color = self.pluginPrefs.get('foregroundColor', '88 88 88')
        foreground_color = f"#{fore_color.replace(' ', '').replace('#', '')}"
        node_color = f"#{self.pluginPrefs.get('nodeColor', 'FF FF FF').replace(' ', '')}"
        nd_clr_border = self.pluginPrefs.get('nodeBorderColor', '66 FF 00')
        node_color_border = f"#{nd_clr_border.replace(' ', '').replace('#', '')}"
        node_marker = self.pluginPrefs.get('nodeMarker', '.')
        node_marker_edge_width = self.pluginPrefs.get('nodeMarkerEdgewidth', '1')
        file_path = (
            '/Library/Application Support/Perceptive Automation/Indigo 2022.1/IndigoWebServer/'
            'images/controls/static/neighbors.png'
        )
        output_file    = self.pluginPrefs.get('chartPath', file_path)
        tick_font_size = int(self.pluginPrefs.get('tickLabelFont', 6))
        x_axis_label   = self.pluginPrefs.get('xAxisLabel', 'node')
        x_axis_rotate  = int(self.pluginPrefs.get('xAxisRotate', 0))
        y_axis_label   = self.pluginPrefs.get('yAxisLabel', 'neighbor')

        # If True, each node that is battery powered will be highlighted.
        plot_battery = self.pluginPrefs.get('plotBattery', False)
        battery_color = (
            self.pluginPrefs.get('plotBatteryColor', 'FF 00 00').replace(' ', '').replace('#', '')
        )
        plot_battery_color = f"#{battery_color}"

        # If True, devices with node 1 missing will be highlighted.
        plot_no_node_1 = self.pluginPrefs.get('plotNoNode1', False)
        node_color_1 = (
            self.pluginPrefs.get('plotNoNode1Color', 'FF 00 00').replace(' ', '').replace('#', '')
        )
        plot_no_node_1_color = f"#{node_color_1}"

        # If True, neighbors without a corresponding node will be highlighted.
        plot_no_node = self.pluginPrefs.get('plotNoNode', False)
        no_node_color = (
            self.pluginPrefs.get('plotNoNodeColor', '00 33 FF').replace(' ', '').replace('#', '')
        )
        plot_no_node_color = f"#{no_node_color}"

        # If True, each node will be plotted as its own neighbor.
        plot_self = self.pluginPrefs.get('plotOwnNodes', False)
        own_node_color = (
            self.pluginPrefs.get('plotOwnNodesColor', '33 33 33').replace(' ', '').replace('#', '')
        )
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
        lost_device        = self.pluginPrefs.get(
            'plotLostDevicesColor', '66 00 CC').replace(' ', '').replace('#', '')
        lost_devices_color = f"#{lost_device}"

        # ================================== kwargs ===================================
        kwarg_savefig = {
            'bbox_extra_artists': None,
            'dpi': int(self.pluginPrefs.get('chartResolution', 100)),
            'edgecolor': background_color,
            'facecolor': background_color,
            'format': None,
            'frameon': None,
            'orientation': None,
            'pad_inches': 0.1,
            'papertype': None,
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
            plt.figure(figsize=(chart_height, chart_width))

        # ========================== Build Master Dictionary ==========================
        # Build the master dictionary of the Z-Wave Mesh Network.
        counter       = 1
        device_dict   = {}
        neighbor_list = []

        # Iterate through all the Z-Wave devices and build a master dictionary.
        for dev in indigo.devices.itervalues('indigo.zwave'):

            dev_address = int(dev.address)
            neighbors   = list(dev.globalProps[self.plugin_id].get('zwNodeNeighbors', []))

            # New device address
            if dev_address not in device_dict:
                device_dict[dev_address] = {}

                device_dict[dev_address]['battery'] = (
                    dev.globalProps[self.plugin_id].get('SupportsBatteryLevel', False)
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
                    dev.globalProps[self.plugin_id].get('SupportsBatteryLevel', False)
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

        # Add a counter value to each device which is used to display a compressed X axis (show
        # unused nodes = False)
        counter = 1
        for key in sorted(device_dict):
            device_dict[key]['counter'] = counter
            counter += 1

        # Dummy dict of devices for testing.  # FIXME - comment out before release
        from dummy_dict import test_file as device_dict  # pylint: disable=unused-wildcard-import
        dev_keys = list(device_dict.keys())

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
            device_delta = (datetime.datetime.now() - device_dict[node]['changed'])
            if device_delta > datetime.timedelta(days=update_delta):
                self.logger.warning(
                    f"Lost Device - {node} [Node {device_dict[node]['name']}] {device_delta}"
                )
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
        plt.tick_params(
            axis='both', which='both', labelsize=tick_font_size, color=foreground_color
        )

        # ============================== X Axis Settings ==============================
        plt.xlabel(
            x_axis_label, fontname=font_name, fontsize=chart_title_font, color=foreground_color
        )
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
        plt.ylabel(
            y_axis_label, fontname=font_name, fontsize=chart_title_font, color=foreground_color
        )
        plt.tick_params(axis='y', left=True, right=False)

        if plot_unused_nodes:
            plt.yticks(
                np.arange(1, max(dev_keys) + 1, 1), fontsize=tick_font_size, color=foreground_color
            )
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

            if plot_no_node_1:
                legend_labels.append("no node 1")
                legend_styles.append(
                    tuple(plt.plot([], color=plot_no_node_1_color, linestyle='', marker='x',
                                   markerfacecolor=plot_no_node_1_color)
                          )
                )

            legend = plt.legend(
                legend_styles, legend_labels, bbox_to_anchor=(1, 0.5), fancybox=True, loc='best',
                ncol=1, numpoints=1, prop={'family': font_name, 'size': 6.5}
            )
            legend.get_frame().set_alpha(0)
            _ = [text.set_color(font_color) for text in legend.get_texts()]

        # =================== Color labels for nodes with no node 1 ===================
        # Affects labels on the X axis.
        if plot_no_node_1:
            x_tick_labels = list(plt.gca().get_xticklabels())

            if plot_unused_nodes:
                for node in dev_keys:
                    if device_dict[node]['no_node_1']:
                        x_tick_labels[node - 1].set_color(plot_no_node_1_color)

            else:
                for node in dev_keys:
                    if device_dict[node]['no_node_1']:
                        x_tick_labels[dev_keys.index(node)].set_color(plot_no_node_1_color)  # noqa

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
            plt.savefig(output_file, **kwarg_savefig)
        except Exception:  # noqa
            self.logger.debug("Chart output error.", exc_info=True)
            self.logger.warning("Chart output error")

        # Wind things up.
        plt.close('all')
        self.logger.info("Z-Wave Node Matrix generated.")

    # =============================================================================
    def make_the_matrix_action(self, values_dict):  # noqa
        """
        Respond to menu call to generate a new image

        When the user calls for an updated image to be generated via the Refresh Matrix menu item,
        call self.make_the_matrix() method.

        :param indigo.Dict values_dict:
        :return:
        """
        self.make_the_matrix()
