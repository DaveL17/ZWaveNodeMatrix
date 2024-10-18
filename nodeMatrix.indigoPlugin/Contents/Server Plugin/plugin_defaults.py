from constants import *

"""
Note that all text field values should be instantiated as strings. If not, the server will coerce the plugin pref to be
of the appropriate type which causes unusual things to happen. For example, if the field pref is set to `integer`, if
you enter a string in the dialog, Indigo will convert it to an integer anyway (i.e., "A" becomes 0).
"""

kDefaultPluginPrefs = {
    'backgroundColor': "00 00 00",
    'chartHeight': "7",
    'chartManualSize': False,
    'chartPath': f"{INSTALL_PATH}/Web Assets/images/controls/static/neighbors.png",
    'chartResolution': "100",
    'chartTitle': "Z-Wave Node Matrix",
    'chartTitleFont': "9",
    'chartWidth': "7",
    'fontMain': "Arial",
    'foregroundColor': "88 88 88",
    'nodeBorderColor': "66 FF 00",
    'nodeColor': "FF FF FF",
    'nodeMarker': ".",
    'nodeMarkerEdgewidth': "1.0",
    'plotBattery': False,
    'plotBatteryColor': "66 00 CC",
    'plotLostDevices': False,
    'plotLostDevicesColor': "FF 00 00",
    'plotLostDevicesTimeDelta': "7",
    'plotNoNode': False,
    'plotNoNode1': False,
    'plotNoNode1Color': "FF 00 00",
    'plotNoNodeColor': "00 33 FF",
    'plotOwnNodes': False,
    'plotOwnNodesColor': "33 33 33",
    'plotUnusedNodes': False,
    'showDebugLevel': "30",
    'showLegend': False,
    'tickLabelFont': "6",
    'xAxisLabel': "node",
    'xAxisRotate': "0",
    'yAxisLabel': "neighbor",
}
