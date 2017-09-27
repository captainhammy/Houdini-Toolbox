"""This module contains data for UI menu items."""

# =============================================================================
# GLOBALS
# =============================================================================

DEFAULT_VALUES = {
    "componentexport": False,
    "lightexport": "",
    "quantize": "half",
    "pfilter": "",
    "priority": -1,
    "sfilter": "alpha",
    "vextype": "vector",
}

LIGHTEXPORT_MENU_ITEMS = (
    ("", "No light exports"),
    ("per-light", "Export variable for each light"),
    ("single", "Merge all lights into single channel"),
    ("per-category", "Export variable for each category"),
)

PFILTER_MENU_ITEMS = (
    ("Inherit from main plane", ""),
    ("Unit Box Filter", "box -w 1"),
    ("Gaussian 2x2", "gaussian -w 2"),
    ("Gaussian 3x3 (softer)", "gaussian -w 3"),
    ("Gaussian 2x2 with noisy sample refiltering", "gaussian -w 2 -r 1"),
    ("Ray Histogram Fusion", "combine -t 20.0"),
    ("Bartlett (triangle)", "bartlett -w 2"),
    ("Catmull-Rom", "catrom -w 3"),
    ("Hanning", "hanning -w 2"),
    ("Blackman", "blackman -w 2"),
    ("Sinc (sharpening)", "sinc -w 3"),
    ("Edge Detection Filter", "edgedetect"),
    ("Closest Sample Filter", "minmax min"),
    ("Farthest Sample Filter", "minmax max"),
    ("Disable Edge Antialiasing", "minmax edge"),
    ("Object With Most Pixel Coverage", "minmax ocover"),
    ("Object With Most Pixel Coverage (no filtering)", "minmax idcover"),
)

QUANTIZE_MENU_ITEMS = (
    ("8", "8 bit integer"),
    ("16", "16 bit integer"),
    ("half", "16 bit float"),
    ("float", "32 bit float"),
)

SFILTER_MENU_ITEMS = (
    ("alpha", "Opacity Filtering"),
    ("fullopacity", "Full Opacity Filtering"),
    ("closest", "Closest Surface"),
)

VEXTYPE_MENU_ITEMS = (
    ("float", "Float Type"),
    ("vector", "Vector Type"),
    ("vector4", "Vector4 Type"),
    ("unitvector", "Unit Vector Type"),
)

# =============================================================================
# STYLES
# =============================================================================

# Style for AOVViewerToolBar.
AOVVIEWERTOOLBAR_STYLE = """
AOVViewerToolBar
{
    border: 0;
}
"""

# Generic tooltip style.
TOOLTIP_STYLE = """
QToolTip {
    background-color: black;
    color: white;
    border: 1px solid black;
}
"""

