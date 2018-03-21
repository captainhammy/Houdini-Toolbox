"""This module contains data for UI menu items."""

# =============================================================================
# GLOBALS
# =============================================================================

DEFAULT_VALUES = {
    "channel": "",
    "components": "diffuse reflect sss",
    "export_components": "",
    "lightexport": "",
    "quantize": "half",
    "pfilter": "",
    "priority": -1,
    "sfilter": "alpha",
    "vextype": "vector",
    "source": "file"
}

LIGHTEXPORT_MENU_ITEMS = (
    ("", "No light exports"),
    ("per-light", "Export variable for each light"),
    ("single", "Merge all lights into single channel"),
    ("per-category", "Export variable for each category"),
)

COMPONENT_MENU_ITEMS = (
    ("diffuse reflect sss", "Basic Components"),
    ("diffuse reflect coat refract volume sss", "Common Components")
)

EXPORT_COMPONENTS = (
    ("", "None"),
    ("rop", "From ROP"),
    ("aov", "In AOV"),
)

PFILTER_MENU_ITEMS = (
    ("", "Inherit from main plane"),
    ("box -w 1", "Unit Box Filter"),
    ("gaussian -w 2", "Gaussian 2x2"),
    ("gaussian -w 3", "Gaussian 3x3 (softer)"),
    ("gaussian -w 2 -r 1", "Gaussian 2x2 with noisy sample refiltering"),
    ("combine -t 20.0", "Ray Histogram Fusion"),
    ("bartlett -w 2", "Bartlett (triangle)"),
    ("catrom -w 3", "Catmull-Rom"),
    ("hanning -w 2", "Hanning"),
    ("blackman -w 2", "Blackman"),
    ("sinc -w 3", "Sinc (sharpening)"),
    ("edgedetect", "Edge Detection Filter"),
    ("minmax min", "Closest Sample Filter"),
    ("minmax max", "Farthest Sample Filter"),
    ("minmax edge", "Disable Edge Antialiasing"),
    ("minmax ocover", "Object With Most Pixel Coverage (average)"),
    ("minmax idcover", "Object With Most Coverage (no filtering)"),
    ("minmax omin", "Object With Most Coverage (minimum z-value)"),
    ("minmax omax", "Object With Most Coverage (maximum z-value)"),
    ("minmax omedian", "Object With Most Coverage (median z-value)"),
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

SOURCE_MENU_ITEMS = (
    ("file", "Disk File"),
    ("group", "AOV Group"),
    ("otl", "Digital Asset"),
    ("hip", "Hip File"),
    ("unsaved", "Unsaved")
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

