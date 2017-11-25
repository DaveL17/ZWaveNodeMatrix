#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Z-Wave Node Matrix Plugin
author: DaveL17

Only tested to be compatible with matplotlib v1.5.3 and Indigo v7
"""

# =================================== TO DO ===================================

# TODO: Add indigo plugin update checker.

# ================================== IMPORTS ==================================

# Built-in modules
import datetime
import logging
import sys
import traceback
try:
    import matplotlib.font_manager as fnt
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as error:
    logging.critical(u'Import Error: {0}'.format(error))
    sys.exit(u"The matplotlib and numpy modules are required to use this script.")

# Third-party modules
from DLFramework import indigoPluginUpdateChecker
try:
    import indigo
except ImportError:
    pass

try:
    import pydevd
except ImportError:
    pass

# My modules
import DLFramework.DLFramework as Dave

# =================================== HEADER ==================================

__author__    = Dave.__author__
__copyright__ = Dave.__copyright__
__license__   = Dave.__license__
__build__     = Dave.__build__
__title__     = 'Z-Wave Node Matrix Plugin'
__version__   = '0.2.6'

# =============================================================================

kDefaultPluginPrefs = {
    u'backgroundColor': "00 00 00",
    u'chartHeight': 7,
    u'chartManualSize': False,
    u'chartPath': "/Library/Application Support/Perceptive Automation/Indigo 7/IndigoWebServer/images/controls/static/neighbors.png",
    u'chartResolution': 100,
    u'chartTitle': "Z-Wave Node Matrix",
    u'chartTitleFont': 9,
    u'chartWidth': 7,
    u'fontMain': "Arial",
    u'foregroundColor': "88 88 88",
    u'nodeBorderColor': "66 FF 00",
    u'nodeColor': "FF FF FF",
    u'nodeMarker': ".",
    u'nodeMarkerEdgewidth': "1.0",
    u'plotBattery': False,
    u'plotBatteryColor': "66 00 CC",
    u'plotLostDevices': False,
    u'plotLostDevicesColor': "FF 00 00",
    u'plotLostDevicesTimeDelta': 7,
    u'plotNoNode': False,
    u'plotNoNode1': False,
    u'plotNoNode1Color': "FF 00 00",
    u'plotNoNodeColor': "00 33 FF",
    u'plotOwnNodes': False,
    u'plotOwnNodesColor': "33 33 33",
    u'plotUnusedNodes': False,
    u'showDebugLevel': 30,
    u'showLegend': False,
    u'tickLabelFont': 6,
    u'updaterEmail': "",
    u'updaterEmailsEnabled': False,
    u'xAxisLabel': "node",
    u'xAxisRotate': 0,
    u'yAxisLabel': "neighbor",
}

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.updater = indigoPluginUpdateChecker.updateChecker(self, "https://github.com/DaveL17/ZWaveNodeMatrix/node_matrix_version.html")
        self.debugLevel = int(self.pluginPrefs.get('showDebugLevel', '30'))
        self.plugin_file_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d\t%(levelname)-10s\t%(name)s.%(funcName)-28s %(msg)s', datefmt='%Y-%m-%d %H:%M:%S'))
        self.debug = True
        self.shutdown = False
        self.indigo_log_handler.setLevel(self.debugLevel)

        # ====================== Initialize DLFramework =======================

        self.Fogbert = Dave.Fogbert(self)

        # Log pluginEnvironment information when plugin is first started
        self.Fogbert.pluginEnvironment()

        # Convert old debugLevel scale (low, medium, high) to new scale (1, 2, 3).
        # if not 0 < self.pluginPrefs.get('showDebugLevel', 1) <= 3:
        #     self.pluginPrefs['showDebugLevel'] = self.Fogbert.convertDebugLevel(self.pluginPrefs['showDebugLevel'])

        # =====================================================================

        # try:
        #     pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
        # except:
        #     pass

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def closedPrefsConfigUi(self, valuesDict, userCancelled):

        pass
        # if not userCancelled:
        #     self.makeTheMatrix()

    def getFontList(self, filter="", typeId=0, valuesDict=None, targetId=0):
        """Generates and returns a list of available fonts.  Note that these
        are the fonts that Matplotlib can see, not necessarily all of the fonts
        installed on the system."""

        from os import path
        counter         = 0
        font_list       = fnt.findSystemFonts(fontpaths=None, fontext='ttf')
        final_font_list = []
        names           = []

        for font in font_list:
            font_name = path.splitext(path.basename(font))[0]
            if font_name not in names:
                names.append(font_name)
        for font in names:
            final_font_list.append((counter, font))
            counter += 1

        return sorted(names)

    def makeTheMatrixAction(self, valuesDict):

        self.makeTheMatrix()

    def makeTheMatrix(self):
        background_color       = r"#{0}".format(self.pluginPrefs.get('backgroundColor', '00 00 00').replace(' ', ''))
        chart_title            = self.pluginPrefs.get('chartTitle', 'Z-Wave Node Matrix')
        chart_title_font       = int(self.pluginPrefs.get('chartTitleFont', 9))
        font_color             = r"#{0}".format(self.pluginPrefs.get('foregroundColor', '88 88 88').replace(' ', ''))
        font_name              = self.pluginPrefs.get('fontMain', 'Arial')
        foreground_color       = r"#{0}".format(self.pluginPrefs.get('foregroundColor', '88 88 88').replace(' ', ''))
        node_color             = r"#{0}".format(self.pluginPrefs.get('nodeColor', 'FF FF FF').replace(' ', ''))
        node_color_border      = r"#{0}".format(self.pluginPrefs.get('nodeBorderColor', '66 FF 00').replace(' ', ''))
        node_marker            = self.pluginPrefs.get('nodeMarker', '.')
        node_marker_edge_width = self.pluginPrefs.get('nodeMarkerEdgewidth', '1')
        output_file            = self.pluginPrefs.get('chartPath', '/Library/Application Support/Perceptive Automation/Indigo 7/IndigoWebServer/images/controls/static/neighbors.png')
        tick_font_size         = int(self.pluginPrefs.get('tickLabelFont', 6))
        x_axis_label           = self.pluginPrefs.get('xAxisLabel', 'node')
        x_axis_rotate          = int(self.pluginPrefs.get('xAxisRotate', 0))
        y_axis_label           = self.pluginPrefs.get('yAxisLabel', 'neighbor')

        # If True, each node that is battery powered will be highlighted.
        plot_battery           = self.pluginPrefs.get('plotBattery', False)
        plot_battery_color     = r"#{0}".format(self.pluginPrefs.get('plotBatteryColor', 'FF 00 00').replace(' ', ''))

        # If True, devices with node 1 missing will be highlighted.
        plot_no_node_1         = self.pluginPrefs.get('plotNoNode1', False)
        plot_no_node_1_color   = r"#{0}".format(self.pluginPrefs.get('plotNoNode1Color', 'FF 00 00').replace(' ', ''))

        # If True, neighbors without a corresponding node will be highlighted.
        plot_no_node           = self.pluginPrefs.get('plotNoNode', False)
        plot_no_node_color     = r"#{0}".format(self.pluginPrefs.get('plotNoNodeColor', '00 33 FF').replace(' ', ''))

        # If True, each node will be plotted as its own neighbor.
        plot_self              = self.pluginPrefs.get('plotOwnNodes', False)
        plot_self_color        = r"#{0}".format(self.pluginPrefs.get('plotOwnNodesColor', '33 33 33').replace(' ', ''))

        # If True, unused node addresses will be plotted.
        plot_unused_nodes      = self.pluginPrefs.get('plotUnusedNodes', False)

        # If True, display a chart legend.
        show_legend            = self.pluginPrefs.get('showLegend', False)

        # If True, the plugin settings will override chart sizing.
        override_chart_size    = self.pluginPrefs.get('chartManualSize', False)

        # If True, the plugin will highlight devices that have not been updated in a user-specified time (days.)
        lost_devices           = self.pluginPrefs.get('plotLostDevices', False)
        update_delta           = int(self.pluginPrefs.get('plotLostDevicesTimeDelta', 7))
        lost_devices_color     = r"#{0}".format(self.pluginPrefs.get('plotLostDevicesColor', "66 00 CC").replace(' ', ''))

        # =================== kwarg Settings ===================
        kwarg_savefig = {'bbox_extra_artists': None,
                         # 'bbox_inches': 'tight',
                         'dpi': int(self.pluginPrefs.get('chartResolution', 100)),
                         'edgecolor': background_color,
                         'facecolor': background_color,
                         'format': None,
                         'frameon': None,
                         'orientation': None,
                         'pad_inches': 0.1,
                         'papertype': None,
                         'transparent': True}
        kwarg_title = {'color': font_color,
                       'fontname': font_name,
                       'fontsize': chart_title_font}

        if override_chart_size:
            chart_height = int(self.pluginPrefs.get('chartHeight', 7))
            chart_width  = int(self.pluginPrefs.get('chartWidth', 7))
            plt.figure(figsize=(chart_height, chart_width))

        # Build the master dictionary of the Z-Wave Mesh Network.
        address_list     = []
        final_devices    = []
        neighbor_list    = []
        no_node_1        = []
        max_addr         = 0
        supports_battery = []

        # Iterate through all the Z-Wave devices and build a list.
        for dev in indigo.devices.itervalues('indigo.zwave'):
            try:
                try:
                    neighbor_list = list(dev.globalProps['com.perceptiveautomation.indigoplugin.zwave']['zwNodeNeighbors'])
                # This is an expected error (not every device will have all of these keys).
                except KeyError as sub_error:
                    self.pluginErrorHandler(traceback.format_exc())
                    self.logger.threaddebug(u"{0}: {1}".format(dev.name, sub_error))

                try:
                    supports_battery = dev.globalProps['com.perceptiveautomation.indigoplugin.zwave']['SupportsBatteryLevel']
                # This is an expected error (not every device will have all of these keys).
                except KeyError as sub_error:
                    self.pluginErrorHandler(traceback.format_exc())
                    self.logger.threaddebug(u"{0}: {1}".format(dev.name, sub_error))

                last_changed = dev.lastChanged

                if int(dev.address) not in address_list:
                    address_list.append(int(dev.address))
                    final_devices.append([int(dev.address), dev.name, neighbor_list, supports_battery, last_changed])

                if max_addr < int(dev.address):
                    max_addr = int(dev.address)

            except Exception as sub_error:
                self.pluginErrorHandler(traceback.format_exc())
                self.logger.threaddebug(u"{0}: {1}".format(dev.name, sub_error))

        # Take the master list, sort it, and add a counter element for later charting.
        counter = 1
        for item in sorted(final_devices):
            item.append(counter)
            counter += 1

        # Assign consecutive keys to neighbor nodes for plotting when unused nodes are not plotted.
        # device[0] = dev.address
        # device[1] = dev.name
        # device[2] = neighbor list
        # device[3] = supports battery
        # device[4] = dev.lastChanged
        # device[5] = position with dummy x

        neighbor_list = []
        for device in sorted(final_devices):
            for neighbor in device[2]:
                if neighbor not in neighbor_list:
                    neighbor_list.append(neighbor)
        for device in sorted(final_devices):
            if device[0] not in neighbor_list:
                neighbor_list.append(device[0])

        counter = 1
        dummy_y = {}
        for neighbor in sorted(neighbor_list):
            if neighbor not in dummy_y.keys():
                dummy_y[neighbor] = counter
                counter += 1

        self.logger.threaddebug(u"Address list: {0}".format(address_list))
        self.logger.threaddebug(u"Final Devices: {0}".format(sorted(final_devices)))
        self.logger.threaddebug(u"Dummy Y: {0}".format(dummy_y))

        # ================== Lay Out The Plots ==================
        for device in sorted(final_devices):
            try:

                # Provide an additional overlay for devices that don't report node 1 as a neighbor.
                if plot_no_node_1 and not device[2]:
                    self.logger.info(u'Device {0} is valid, but has no neighbors. Skipping.'.format(device[0]))
                elif plot_no_node_1 and device[2][0] != 1 and plot_unused_nodes:
                    [no_node_1.append(int(device[5]) - 1) for _ in device[2]]

                elif plot_no_node_1 and device[2][0] != 1 and not plot_unused_nodes:
                    [no_node_1.append(int(device[5]) - 1) for _ in device[2]]

                # This plot will show all Z-Wave neighbors on the plot.
                if plot_unused_nodes:
                    for neighbor in device[2]:
                        plt.plot(device[0], neighbor, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=node_color_border, markerfacecolor=node_color,
                                 zorder=10)
                else:
                    for neighbor in device[2]:
                        plt.plot(device[5], dummy_y[neighbor], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=node_color_border, markerfacecolor=node_color,
                                 zorder=10)

                # This plot provides an overlay for battery devices.
                if device[3] and plot_battery and plot_unused_nodes:
                    for neighbor in device[2]:
                        plt.plot(device[0], neighbor, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_battery_color, markerfacecolor=node_color,
                                 zorder=10)
                elif device[3] and plot_battery:
                    for neighbor in device[2]:
                        plt.plot(device[5], dummy_y[neighbor], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_battery_color,
                                 markerfacecolor=node_color, zorder=10)

                if lost_devices:
                    x_delta = (datetime.datetime.now() - device[4])
                    if x_delta > datetime.timedelta(days=update_delta):
                        self.logger.warning(u"Lost Device: {0}: {1}".format(device[1], x_delta))

                        for neighbor in device[2]:
                            plt.plot(device[5], dummy_y[neighbor], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=lost_devices_color,
                                     markerfacecolor=node_color, zorder=10)

                # This plot will assign a point to a node for its own address (plot itself.)
                if plot_self and plot_unused_nodes:
                    for me in np.arange(2, max_addr, 1):
                        plt.plot(me, me, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_self_color, markerfacecolor=plot_self_color, zorder=10)
                elif plot_self:
                    plt.plot(device[5], dummy_y[device[0]], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_self_color,
                             markerfacecolor=plot_self_color, zorder=10)

            except IndexError:
                self.pluginErrorHandler(traceback.format_exc())

            except KeyError as sub_error:
                self.pluginErrorHandler(traceback.format_exc())
                self.logger.warning(u"{0} - {1}. Skipping.".format(device[0], sub_error))

            except Exception as sub_error:
                self.pluginErrorHandler(traceback.format_exc())
                self.logger.info(u"{0} - Problem building node matrix: {1}".format(device[0], sub_error))

        # =================== Chart Settings ===================
        plt.title(chart_title, **kwarg_title)
        for spine in ['top', 'bottom', 'left', 'right']:
            plt.gca().spines[spine].set_color(foreground_color)
        plt.tick_params(axis='both', which='both', labelsize=tick_font_size, color=foreground_color)

        # =================== X Axis Settings ===================
        plt.xlabel(x_axis_label, fontsize=chart_title_font, color=foreground_color)
        plt.tick_params(axis='x', bottom=True, top=False)

        if plot_unused_nodes:
            plt.xticks(np.arange(1, max_addr + 1, 1), fontsize=tick_font_size, color=foreground_color, rotation=x_axis_rotate)
            plt.xlim(1, max_addr + 1)
        else:
            plt.xticks(np.arange(1, len(final_devices) + 1, 1), sorted(address_list), fontsize=tick_font_size, color=foreground_color, rotation=x_axis_rotate)
            plt.xlim(0, len(final_devices) + 1)

        # =================== Y Axis Settings ===================
        plt.ylabel(y_axis_label, fontsize=chart_title_font, color=foreground_color)
        plt.tick_params(axis='y', left=True, right=False)

        if plot_unused_nodes:
            plt.yticks(np.arange(1, max_addr + 1, 1), fontsize=tick_font_size, color=foreground_color)
            plt.ylim(0, max_addr + 1)
        else:
            plt.yticks(np.arange(1, max_addr, 1), sorted(dummy_y.keys()), fontsize=tick_font_size, color=foreground_color)
            plt.ylim(0, len(dummy_y) + 1)

        # =================== Legend Settings ===================
        # Legend entries must be tuples.
        if show_legend:
            legend_labels = []
            legend_styles = []

            # Neighbor
            legend_labels.append(u"neighbor")
            legend_styles.append(tuple(plt.plot([], color=node_color_border, linestyle='', marker=node_marker, markerfacecolor=node_color)))

            if plot_battery:
                legend_labels.append(u"battery")
                legend_styles.append(tuple(plt.plot([], color=plot_battery_color, linestyle='', marker=node_marker, markerfacecolor=node_color, markeredgewidth=node_marker_edge_width,
                                                    markeredgecolor=plot_battery_color)))

            if plot_self:
                legend_labels.append(u"self")
                legend_styles.append(tuple(plt.plot([], color=plot_self_color, linestyle='', marker=node_marker, markerfacecolor=plot_self_color)))

            if lost_devices:
                legend_labels.append(u"{0} ({1})".format('lost', update_delta))
                legend_styles.append(tuple(plt.plot([], color=lost_devices_color, linestyle='', marker=node_marker, markeredgewidth=node_marker_edge_width,
                                                    markeredgecolor=lost_devices_color, markerfacecolor=node_color)))

            if plot_no_node:
                legend_labels.append(u"no node")
                legend_styles.append(tuple(plt.plot([], color=plot_no_node_color, linestyle='', marker='x', markerfacecolor=plot_no_node_color)))

            if plot_no_node_1:
                legend_labels.append(u"no node 1")
                legend_styles.append(tuple(plt.plot([], color=plot_no_node_1_color, linestyle='', marker='x', markerfacecolor=plot_no_node_1_color)))

            legend = plt.legend(legend_styles, legend_labels, bbox_to_anchor=(1, 0.5), fancybox=True, loc='best', ncol=1, numpoints=1, prop={'size': 6.5})
            legend.get_frame().set_alpha(0)
            [text.set_color(font_color) for text in legend.get_texts()]

        # ======== Color labels for nodes with no node 1 ========
        if plot_no_node_1 and no_node_1:
            foo_x = [i for i in plt.gca().get_xticklabels()]
            if not plot_unused_nodes:
                for node in no_node_1:
                    foo_x[node].set_color(plot_no_node_1_color)
            else:
                for node in no_node_1:
                    foo = sorted(final_devices)
                    a = foo[node][0]
                    foo_x[a - 1].set_color(plot_no_node_1_color)

        # ========= Color labels for neighbors with no node ========
        if plot_no_node:
            foo_y = [i for i in plt.gca().get_yticklabels()]
            for a in dummy_y.keys():
                if a not in address_list:
                    if a != 1:
                        if not plot_unused_nodes:
                            a = dummy_y[a] - 1
                            foo_y[a].set_color(plot_no_node_color)
                        else:
                            a -= 1
                            foo_y[a].set_color(plot_no_node_color)

        # ========= Output the Z-Wave Node Matrix Image =========
        try:
            plt.savefig(output_file, **kwarg_savefig)
        except Exception as sub_error:
            self.pluginErrorHandler(traceback.format_exc())
            self.logger.info(u"Chart output error: {0}:".format(sub_error))

        # Wind things up.
        plt.close()
        self.logger.info(u"Z-Wave Node Matrix generated.")

    def pluginErrorHandler(self, sub_error):
        """Centralized handling of traceback messages formatted for pretty
        display in the plugin log file. If sent here, they will not be
        displayed in the Indigo Events log. Use the following syntax to
        send exceptions here:
        self.pluginErrorHandler(traceback.format_exc())"""
        sub_error = sub_error.splitlines()
        self.logger.threaddebug(u"{0:!^80}".format(" TRACEBACK "))
        for line in sub_error:
            self.logger.threaddebug(u"!!! {0}".format(line))
        self.logger.threaddebug(u"!" * 80)
        # self.logger.warning(u"Error: {0}".format(sub_error[3]))

    def checkVersionNow(self):
        """ The checkVersionNow() method will call the Indigo Plugin Update
        Checker based on a user request. """
        self.debugLog(u"checkVersionNow() method called.")

        try:
            self.updater.checkVersionNow()
        except Exception as error:
            self.errorLog(u"Error checking plugin update status. Error: {0} (Line {1})".format(error, sys.exc_traceback.tb_lineno))
            return False

    def runConcurrentThread(self):
        # While Indigo hasn't told us to shutdown
        while self.shutdown is False:
            self.updater.checkVersionPoll()
            self.sleep(1)

    def stopConcurrentThread(self):
        self.shutdown = True
