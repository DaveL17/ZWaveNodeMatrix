#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Z-Wave Node Matrix Plugin
author: DaveL17

Only tested to be compatible with matplotlib v1.5.3 and Indigo v7
"""

# =================================== TO DO ===================================
# TODO: New config dialog image for the wiki.

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
__version__   = '1.0.04'

# =============================================================================
install_path = indigo.server.getInstallFolderPath()

kDefaultPluginPrefs = {
    u'backgroundColor': "00 00 00",
    u'chartHeight': 7,
    u'chartManualSize': False,
    u'chartPath': u"{0}/IndigoWebServer/images/controls/static/neighbors.png".format(install_path),
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
    u'xAxisLabel': "node",
    u'xAxisRotate': 0,
    u'yAxisLabel': "neighbor",
}


class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.pluginIsInitializing = True
        self.pluginIsShuttingDown = False

        self.debugLevel = int(self.pluginPrefs.get('showDebugLevel', '30'))
        self.plugin_file_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d\t%(levelname)-10s\t%(name)s.%(funcName)-28s %(msg)s', datefmt='%Y-%m-%d %H:%M:%S'))
        self.debug      = True
        self.indigo_log_handler.setLevel(self.debugLevel)

        # ========================== Initialize DLFramework ===========================

        self.Fogbert = Dave.Fogbert(self)

        # Log pluginEnvironment information when plugin is first started
        self.Fogbert.pluginEnvironment()

        # ============================= Remote Debugging ==============================
        # try:
        #     pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True, suspend=False)
        # except:
        #     pass

        self.pluginIsInitializing = False

    # =============================================================================
    def __del__(self):

        indigo.PluginBase.__del__(self)

    # =============================================================================
    # ============================== Indigo Methods ===============================
    # =============================================================================
    def closedPrefsConfigUi(self, valuesDict, userCancelled):

        self.debugLevel = int(valuesDict['showDebugLevel'])
        self.indigo_log_handler.setLevel(self.debugLevel)

    # =============================================================================
    def runConcurrentThread(self):

        while self.pluginIsShuttingDown is False:
            self.sleep(1)

    # =============================================================================
    def stopConcurrentThread(self):

        self.pluginIsShuttingDown = True

    # =============================================================================
    # ============================== Plugin Methods ===============================
    # =============================================================================
    def get_font_list(self, filter="", typeId=0, valuesDict=None, targetId=0):
        """
        Returns a list of available TrueType fonts

        Generates and returns a list of available fonts.  Note that these
        are the fonts that Matplotlib can see, not necessarily all of the fonts
        installed on the system.

        -----
        :param filter:
        :param typeId:
        :param valuesDict:
        :param targetId:

        :return list names:
        """

        from os import path

        font_list = fnt.findSystemFonts(fontpaths=None, fontext='ttf')
        names     = [path.splitext(path.basename(font))[0] for font in font_list]

        return sorted(names)

    # =============================================================================
    def make_the_matrix(self):
        """
        Generate the Z-Wave node matrix image

        General code to construct the Z-Wave node matrix image.

        -----

        """
        background_color       = r"#{0}".format(self.pluginPrefs.get('backgroundColor', '00 00 00').replace(' ', '').replace('#', ''))
        chart_title            = self.pluginPrefs.get('chartTitle', 'Z-Wave Node Matrix')
        chart_title_font       = int(self.pluginPrefs.get('chartTitleFont', 9))
        font_color             = r"#{0}".format(self.pluginPrefs.get('foregroundColor', '88 88 88').replace(' ', '').replace('#', ''))
        font_name              = self.pluginPrefs.get('fontMain', 'Arial')
        foreground_color       = r"#{0}".format(self.pluginPrefs.get('foregroundColor', '88 88 88').replace(' ', '').replace('#', ''))
        node_color             = r"#{0}".format(self.pluginPrefs.get('nodeColor', 'FF FF FF').replace(' ', ''))
        node_color_border      = r"#{0}".format(self.pluginPrefs.get('nodeBorderColor', '66 FF 00').replace(' ', '').replace('#', ''))
        node_marker            = self.pluginPrefs.get('nodeMarker', '.')
        node_marker_edge_width = self.pluginPrefs.get('nodeMarkerEdgewidth', '1')
        output_file            = self.pluginPrefs.get('chartPath', '/Library/Application Support/Perceptive Automation/Indigo 7/IndigoWebServer/images/controls/static/neighbors.png')
        tick_font_size         = int(self.pluginPrefs.get('tickLabelFont', 6))
        x_axis_label           = self.pluginPrefs.get('xAxisLabel', 'node')
        x_axis_rotate          = int(self.pluginPrefs.get('xAxisRotate', 0))
        y_axis_label           = self.pluginPrefs.get('yAxisLabel', 'neighbor')

        # If True, each node that is battery powered will be highlighted.
        plot_battery           = self.pluginPrefs.get('plotBattery', False)
        plot_battery_color     = r"#{0}".format(self.pluginPrefs.get('plotBatteryColor', 'FF 00 00').replace(' ', '').replace('#', ''))

        # If True, devices with node 1 missing will be highlighted.
        plot_no_node_1         = self.pluginPrefs.get('plotNoNode1', False)
        plot_no_node_1_color   = r"#{0}".format(self.pluginPrefs.get('plotNoNode1Color', 'FF 00 00').replace(' ', '').replace('#', ''))

        # If True, neighbors without a corresponding node will be highlighted.
        plot_no_node           = self.pluginPrefs.get('plotNoNode', False)
        plot_no_node_color     = r"#{0}".format(self.pluginPrefs.get('plotNoNodeColor', '00 33 FF').replace(' ', '').replace('#', ''))

        # If True, each node will be plotted as its own neighbor.
        plot_self              = self.pluginPrefs.get('plotOwnNodes', False)
        plot_self_color        = r"#{0}".format(self.pluginPrefs.get('plotOwnNodesColor', '33 33 33').replace(' ', '').replace('#', ''))

        # If True, unused node addresses will be plotted.
        plot_unused_nodes      = self.pluginPrefs.get('plotUnusedNodes', False)

        # If True, display a chart legend.
        show_legend            = self.pluginPrefs.get('showLegend', False)

        # If True, the plugin settings will override chart sizing.
        override_chart_size    = self.pluginPrefs.get('chartManualSize', False)

        # If True, the plugin will highlight devices that have not been updated in a user-specified time (days.)
        plot_lost_devices      = self.pluginPrefs.get('plotLostDevices', False)
        update_delta           = int(self.pluginPrefs.get('plotLostDevicesTimeDelta', 7))
        lost_devices_color     = r"#{0}".format(self.pluginPrefs.get('plotLostDevicesColor', "66 00 CC").replace(' ', '').replace('#', ''))

        # ================================== kwargs ===================================
        kwarg_savefig = {'bbox_extra_artists': None,
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

        # ========================== Build Master Dictionary ==========================
        # Build the master dictionary of the Z-Wave Mesh Network.
        counter       = 1
        device_dict   = {}
        neighbor_list = []

        # Iterate through all the Z-Wave devices and build a master dictionary.
        for dev in indigo.devices.itervalues('indigo.zwave'):

            dev_address = int(dev.address)
            neighbors   = list(dev.globalProps['com.perceptiveautomation.indigoplugin.zwave'].get('zwNodeNeighbors', []))

            # New device address
            if dev_address not in device_dict.keys():
                device_dict[dev_address] = {}

                device_dict[dev_address]['battery']          = dev.globalProps['com.perceptiveautomation.indigoplugin.zwave'].get('SupportsBatteryLevel', False)
                device_dict[dev_address]['changed']          = dev.lastChanged
                device_dict[dev_address]['invalid_neighbor'] = False
                device_dict[dev_address]['lost']             = False
                device_dict[dev_address]['neighbors']        = neighbors
                device_dict[dev_address]['no_node_1']        = False
                device_dict[dev_address]['name']             = dev.name

                counter += 1

            # Device address already in device_dict but device has neighbors (neighbor list not empty)
            elif dev_address in device_dict.keys() and neighbors:
                device_dict[dev_address]['battery']          = dev.globalProps['com.perceptiveautomation.indigoplugin.zwave'].get('SupportsBatteryLevel', False)
                device_dict[dev_address]['changed']          = dev.lastChanged
                device_dict[dev_address]['invalid_neighbor'] = False
                device_dict[dev_address]['lost']             = False
                device_dict[dev_address]['neighbors']        = neighbors
                device_dict[dev_address]['no_node_1']        = False
                device_dict[dev_address]['name']             = dev.name

            # Device address already in device_dict but device has no neighbors
            else:
                pass

        # Add a counter value to each device which is used to display a compressed X
        # axis (show unused nodes = False)
        counter = 1
        for key in sorted(device_dict):
            device_dict[key]['counter'] = counter
            counter += 1

        # Dummy dict of devices for testing
        # device_dict = {3: {'neighbors': [4, 5, 10, 11, 12, 15, 16, 17, 18, 25, 27, 28, 29, 30, 39, 41, 43], 'counter': 1, 'name': u'Master Bedroom - West Bedside Lamp', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 18, 56, 20), 'no_node_1': False, 'invalid_neighbor': False}, 4: {'neighbors': [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29, 39, 41, 43, 44], 'counter': 2, 'name': u'Foyer - Lamp', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 9, 41), 'no_node_1': False, 'invalid_neighbor': False}, 5: {'neighbors': [3, 4, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 25, 27, 28, 29, 30, 39, 41, 43], 'counter': 3, 'name': u'Outdoor - Front Porch Lights', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 33), 'no_node_1': False, 'invalid_neighbor': False}, 7: {'neighbors': [4, 8, 11, 12, 23, 43, 44], 'counter': 4, 'name': u'Outdoor - Garage Side Door Light', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 34), 'no_node_1': False, 'invalid_neighbor': False}, 8: {'neighbors': [4, 5, 7, 10, 11, 12, 15, 18, 20, 21, 23, 27, 28, 30, 41, 42, 43, 44], 'counter': 5, 'name': u'Garage - Motion', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 16, 18, 4, 5), 'no_node_1': False, 'invalid_neighbor': False}, 10: {'neighbors': [3, 4, 5, 8, 11, 12, 15, 16, 17, 18, 21, 22, 25, 27, 28, 39, 41, 43, 44], 'counter': 6, 'name': u'Living Room - Outlet North', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 9, 34), 'no_node_1': False, 'invalid_neighbor': False}, 11: {'neighbors': [3, 4, 5, 7, 8, 10, 12, 13, 15, 16, 17, 18, 20, 21, 22, 27, 28, 29, 39, 41, 42, 43, 44], 'counter': 7, 'name': u'Thermostat - Downstairs', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 19, 48, 16), 'no_node_1': False, 'invalid_neighbor': False}, 12: {'neighbors': [3, 4, 5, 7, 8, 10, 11, 13, 15, 16, 18, 20, 21, 22, 23, 24, 27, 28, 39, 41, 42, 43], 'counter': 8, 'name': u'Basement - Humidifier', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 30, 1), 'no_node_1': False, 'invalid_neighbor': False}, 14: {'neighbors': [3, 4, 7, 8, 11, 12, 15, 16, 17, 20, 21, 22, 24, 27, 28, 29, 39, 41, 43, 44], 'counter': 9, 'name': u'Dining Room - Motion', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 16, 20, 2, 2), 'no_node_1': False, 'invalid_neighbor': False}, 15: {'neighbors': [3, 4, 5, 8, 10, 11, 12, 16, 17, 18, 21, 22, 25, 27, 28, 29, 39, 41, 43, 44], 'counter': 10, 'name': u'Living Room - Desk Lamp', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 9, 34), 'no_node_1': False, 'invalid_neighbor': False}, 16: {'neighbors': [3, 4, 5, 10, 11, 12, 13, 15, 17, 18, 22, 25, 27, 28, 29, 39, 41, 43, 44], 'counter': 11, 'name': u'Living Room - Vase', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 9, 34), 'no_node_1': False, 'invalid_neighbor': False}, 17: {'neighbors': [3, 5, 10, 13, 15, 16, 22, 39, 41, 43], 'counter': 12, 'name': u'Living Room - TV', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 18, 57, 33), 'no_node_1': False, 'invalid_neighbor': False}, 18: {'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 21, 22, 27, 28, 29, 39, 41, 42, 43], 'counter': 13, 'name': u'Outdoor - Back Porch Light', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 34), 'no_node_1': False, 'invalid_neighbor': False}, 20: {'neighbors': [8, 11, 21, 24, 43], 'counter': 14, 'name': u'Outdoor - Septic Pump', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 53, 28), 'no_node_1': False, 'invalid_neighbor': False}, 21: {'neighbors': [5, 8, 10, 11, 12, 13, 15, 20, 22, 27, 29, 30, 41, 42, 43], 'counter': 15, 'name': u'Kitchen - Cabinets North', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 53, 19), 'no_node_1': False, 'invalid_neighbor': False}, 22: {'neighbors': [4, 5, 10, 11, 12, 15, 16, 17, 21, 27, 28, 29, 41, 43], 'counter': 16, 'name': u'Kitchen - Cabinets South', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 53, 26), 'no_node_1': False, 'invalid_neighbor': False}, 23: {'neighbors': [7, 8, 12, 20], 'counter': 17, 'name': u'Outdoor - Path Lights Rear North', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 34), 'no_node_1': False, 'invalid_neighbor': False}, 24: {'neighbors': [4, 12, 13, 15, 20, 43], 'counter': 18, 'name': u'Outdoor - Path Lights Front North', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 34), 'no_node_1': False, 'invalid_neighbor': False}, 25: {'neighbors': [3, 4, 5, 10, 15, 16, 27, 28, 29, 41, 43], 'counter': 19, 'name': u'Outdoor - Path Lights Front South', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 34), 'no_node_1': False, 'invalid_neighbor': False}, 27: {'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 18, 21, 22, 25, 28, 29, 39, 41, 43], 'counter': 20, 'name': u'Basement - Energy Meter 1', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 45, 6), 'no_node_1': False, 'invalid_neighbor': False}, 28: {'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 17, 18, 22, 25, 27, 29, 39, 41, 42, 43], 'counter': 21, 'name': u'Basement - Energy Meter 2', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 49, 23), 'no_node_1': False, 'invalid_neighbor': False}, 30: {'neighbors': [3, 5, 8, 13, 17, 21, 22, 28, 29, 39, 41, 43], 'counter': 22, 'name': u'Main Attic - Motion', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 14, 12, 52, 6), 'no_node_1': False, 'invalid_neighbor': False}, 31: {'neighbors': [3, 4, 5, 8, 10, 15, 16, 17, 18, 21, 22, 27, 28, 29, 30, 39, 41, 43], 'counter': 23, 'name': u'Outdoor - Luminance', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 16, 20, 42, 29), 'no_node_1': False, 'invalid_neighbor': False}, 32: {'neighbors': [2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 24, 25, 26, 27, 28, 29, 30], 'counter': 24, 'name': u'Foyer - Upstairs Smoke', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 14, 9, 55, 55), 'no_node_1': False, 'invalid_neighbor': False}, 33: {'neighbors': [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30], 'counter': 25, 'name': u'Foyer - Main Floor Smoke', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 16, 16, 27, 24), 'no_node_1': False, 'invalid_neighbor': False}, 34: {'neighbors': [2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 24, 25, 26, 27, 28, 29], 'counter': 26, 'name': u'Basement - Smoke', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 11, 4, 37, 16), 'no_node_1': False, 'invalid_neighbor': False}, 37: {'neighbors': [4, 7, 8, 11, 15, 23, 43], 'counter': 27, 'name': u'Garage - Side Door', 'lost': False, 'battery': True, 'changed': datetime.datetime(2018, 7, 16, 20, 35, 24), 'no_node_1': False, 'invalid_neighbor': False}, 38: {'neighbors': [2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30], 'counter': 28, 'name': u'Guest Bathroom - Exhaust Fan', 'lost': False, 'battery': False, 'changed': datetime.datetime(2017, 10, 28, 10, 18, 5), 'no_node_1': False, 'invalid_neighbor': False}, 39: {'neighbors': [3, 4, 5, 10, 11, 12, 13, 15, 16, 18, 27, 28, 29, 41, 43, 44], 'counter': 29, 'name': u'Master Bedroom - Star Lamp', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 9, 34), 'no_node_1': False, 'invalid_neighbor': False}, 41: {'neighbors': [3, 4, 5, 8, 10, 11, 12, 13, 15, 16, 17, 18, 21, 22, 25, 27, 28, 29, 30, 39, 43, 44], 'counter': 30, 'name': u'Workshop - Fibaro RGBW', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 18, 59, 23), 'no_node_1': False, 'invalid_neighbor': False}, 42: {'neighbors': [8, 11, 12, 13, 21, 43], 'counter': 31, 'name': u'Basement - Dehumidifier', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 43, 17), 'no_node_1': False, 'invalid_neighbor': False}, 43: {'neighbors': [3, 4, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20, 21, 22, 24, 25, 27, 28, 29, 30, 39, 41, 42, 44], 'counter': 32, 'name': u'Thermostat - Upstairs', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 40, 47), 'no_node_1': False, 'invalid_neighbor': False}, 44: {'neighbors': [4, 5, 7, 8, 11, 13, 15, 16, 20, 22, 39, 41, 43], 'counter': 33, 'name': u'Outdoor - Garage Driveway Lights', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 21, 33), 'no_node_1': False, 'invalid_neighbor': False}, 45: {'neighbors': [3, 4, 13, 15, 28, 41, 43], 'counter': 34, 'name': u'Main Attic - Ventilation Fan', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 0, 37), 'no_node_1': False, 'invalid_neighbor': False}, 46: {'neighbors': [3, 4, 16, 41, 43], 'counter': 35, 'name': u'Basement - Cable Modem', 'lost': False, 'battery': False, 'changed': datetime.datetime(2018, 7, 16, 20, 50, 24), 'no_node_1': False, 'invalid_neighbor': False}}

        dev_keys = device_dict.keys()

        # ======================= Update Device Characteristics =======================
        for node in dev_keys:

            # No node 1 in neighbor list
            if 1 not in device_dict[node]['neighbors']:
                device_dict[node]['no_node_1'] = True

            # Device is lost
            device_delta = (datetime.datetime.now() - device_dict[node]['changed'])
            if device_delta > datetime.timedelta(days=update_delta):
                self.logger.warning(u"Lost Device - {1} [Node {0}] {2}".format(node, device_dict[node]['name'], device_delta))
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

        # dummy_y for use in compressing the Y axis.  It's currently unused
        dummy_y = {node: counter for counter, node in enumerate(neighbor_list, 1)}

        self.logger.debug(u"Device Dict: {0}".format(device_dict))

        # ============================= Lay Out The Plots =============================
        for node in dev_keys:

            # ================================= Plot Self =================================
            if plot_self:
                if plot_unused_nodes:
                    plt.plot(node, node, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_self_color, markerfacecolor=node_color, zorder=11)
                else:
                    plt.plot(device_dict[node]['counter'], dummy_y[node], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_self_color,
                             markerfacecolor=node_color, zorder=11)

            # ============================ Plot Neighbors =============================
            for neighbor in device_dict[node]['neighbors']:
                if plot_unused_nodes:
                    plt.plot(node, neighbor, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=node_color_border, markerfacecolor=node_color, zorder=9)
                else:
                    plt.plot(device_dict[node]['counter'], dummy_y[neighbor], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=node_color_border,
                             markerfacecolor=node_color, zorder=9)

                # =========================== Plot Battery Devices ============================
                if plot_battery:
                    if plot_unused_nodes and device_dict[node]['battery']:
                        plt.plot(node, neighbor, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_battery_color, markerfacecolor=node_color, zorder=10)
                    elif device_dict[node]['battery']:
                        plt.plot(device_dict[node]['counter'], dummy_y[neighbor], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=plot_battery_color,
                                 markerfacecolor=node_color, zorder=10)

                # ============================= Plot Lost Devices =============================
                if plot_lost_devices and device_dict[node]['lost']:
                    if plot_unused_nodes:
                        plt.plot(node, neighbor, marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=lost_devices_color, markerfacecolor=node_color, zorder=11)
                    else:
                        plt.plot(device_dict[node]['counter'], dummy_y[neighbor], marker=node_marker, markeredgewidth=node_marker_edge_width, markeredgecolor=lost_devices_color,
                                 markerfacecolor=node_color, zorder=11)

        # ============================== Chart Settings ===============================
        plt.title(chart_title, **kwarg_title)
        for spine in ('top', 'bottom', 'left', 'right'):
            plt.gca().spines[spine].set_color(foreground_color)
        plt.tick_params(axis='both', which='both', labelsize=tick_font_size, color=foreground_color)

        # ============================== X Axis Settings ==============================
        plt.xlabel(x_axis_label, fontname=font_name, fontsize=chart_title_font, color=foreground_color)
        plt.tick_params(axis='x', bottom=True, top=False)

        if plot_unused_nodes:
            plt.xticks(np.arange(1, max(dev_keys) + 1, 1), fontname=font_name, fontsize=tick_font_size, color=foreground_color, rotation=x_axis_rotate)
            plt.xlim(1, max(dev_keys) + 1)
        else:
            plt.xticks(np.arange(1, len(device_dict) + 1, 1), sorted(dev_keys), fontname=font_name, fontsize=tick_font_size, color=foreground_color, rotation=x_axis_rotate)
            plt.xlim(0, len(device_dict) + 1)

        # ============================== Y Axis Settings ==============================
        plt.ylabel(y_axis_label, fontname=font_name, fontsize=chart_title_font, color=foreground_color)
        plt.tick_params(axis='y', left=True, right=False)

        if plot_unused_nodes:
            plt.yticks(np.arange(1, max(dev_keys) + 1, 1), fontsize=tick_font_size, color=foreground_color)
            plt.ylim(0, max(dev_keys) + 1)
        else:
            plt.yticks(np.arange(1, max(dev_keys), 1), sorted(dummy_y.keys()), fontsize=tick_font_size, color=foreground_color)
            plt.ylim(0, len(dummy_y) + 1)

        # ============================== Legend Settings ==============================
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
                legend_styles.append(tuple(plt.plot([], color=plot_self_color, linestyle='', marker=node_marker, markerfacecolor=node_color, markeredgecolor=plot_self_color)))

            if plot_lost_devices:
                legend_labels.append(u"{0} ({1})".format('lost', update_delta))
                legend_styles.append(tuple(plt.plot([], color=lost_devices_color, linestyle='', marker=node_marker, markeredgewidth=node_marker_edge_width,
                                                    markeredgecolor=lost_devices_color, markerfacecolor=node_color)))

            if plot_no_node:
                legend_labels.append(u"no node")
                legend_styles.append(tuple(plt.plot([], color=plot_no_node_color, linestyle='', marker='x', markerfacecolor=plot_no_node_color)))

            if plot_no_node_1:
                legend_labels.append(u"no node 1")
                legend_styles.append(tuple(plt.plot([], color=plot_no_node_1_color, linestyle='', marker='x', markerfacecolor=plot_no_node_1_color)))

            legend = plt.legend(legend_styles, legend_labels, bbox_to_anchor=(1, 0.5), fancybox=True, loc='best', ncol=1, numpoints=1, prop={'family': font_name, 'size': 6.5})
            legend.get_frame().set_alpha(0)
            [text.set_color(font_color) for text in legend.get_texts()]

        # =================== Color labels for nodes with no node 1 ===================
        # Affects labels on the X axis.

        if plot_no_node_1:
            x_tick_labels = [i for i in plt.gca().get_xticklabels()]

            if plot_unused_nodes:
                for node in dev_keys:
                    if device_dict[node]['no_node_1']:
                        x_tick_labels[node - 1].set_color(plot_no_node_1_color)

            else:
                for node in dev_keys:
                    if device_dict[node]['no_node_1']:
                        x_tick_labels[dev_keys.index(node)].set_color(plot_no_node_1_color)

        # ================== Color labels for neighbors with no node ==================
        # Affects labels on the Y axis.
        if plot_no_node:
            y_tick_labels = [i for i in plt.gca().get_yticklabels()]

            for a in dummy_y.keys():
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
        except Exception as sub_error:
            self.plugin_error_handler(traceback.format_exc())
            self.logger.warning(u"Chart output error: {0}:".format(sub_error))

        # Wind things up.
        plt.close('all')
        self.logger.info(u"Z-Wave Node Matrix generated.")

    # =============================================================================
    def make_the_matrix_action(self, valuesDict):
        """
        Respond to menu call to generate a new image

        When the user calls for an updated image to be generated via the Refresh Matrix
        menu item, call self.make_the_matrix() method.

        -----

        :param valuesDict:

        """
        self.make_the_matrix()

    # =============================================================================
    def plugin_error_handler(self, sub_error):
        """
        General handling of trapped plugin exceptions

        Centralized handling of traceback messages formatted for pretty
        display in the plugin log file. If sent here, they will not be
        displayed in the Indigo Events log. Use the following syntax to
        send exceptions here:
        self.plugin_error_handler(traceback.format_exc())

        -----

        :param sub_error:
        """

        sub_error = sub_error.splitlines()
        self.logger.threaddebug(u"{0:!^80}".format(" TRACEBACK "))

        for line in sub_error:
            self.logger.threaddebug(u"!!! {0}".format(line))
        self.logger.threaddebug(u"!" * 80)
