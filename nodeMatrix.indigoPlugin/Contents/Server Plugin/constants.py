"""
Repository of application constants

The constants.py file contains all application constants and is imported as a library. References
are denoted as constants by the use of all caps.
"""
try:
    import indigo
except ImportError:
    pass


def __init__():
    pass


DEBUG_LABELS = {
    10: "Debugging Messages",
    20: "Informational Messages",
    30: "Warning Messages",
    40: "Error Messages",
    50: "Critical Errors Only"
}

INSTALL_PATH = indigo.server.getInstallFolderPath()
