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

# Style for custom MenuField widget.
MENUFIELD_STYLE = """
QPushButton
{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0.0 rgb(63, 63, 63),
                                stop: 1.0 rgb(38, 38, 38));

    height: 14px;
    width: 11px;
    border: 1px solid rgba(0,0,0,102);

}

QPushButton::menu-indicator
{
    subcontrol-position: center;
    height: 16;
    width: 6;
}
"""

# Style for CustomSpinBox widget.
CUSTOMSPINBOX_STYLE = """
CustomSpinBox {
    border: 1px solid rgba(0,0,0,102);
    border-radius: 1px;
    background: rgb(19, 19, 19);
    selection-color: rgb(0, 0, 0);
    selection-background-color: rgb(184, 134, 32);
}

CustomSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right; /* position at the top right corner */
    width: 16px;
    border-width: 1px;
    background: rgb(38, 38, 38);
    width: 20px;
}

CustomSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right; /* position at bottom right corner */
    border-image: url(:/images/spindown.png) 1;
    border-width: 1px;
    border-top-width: 0;
    background: rgb(38, 38, 38);
    width: 20px;
 }

CustomSpinBox::up-arrow {
    image: url(:ht/rsc/icons/aovs/button_up.png) 1;
    width: 14px;
    height: 14px;
}

CustomSpinBox::down-arrow
{
    image: url(:ht/rsc/icons/aovs/button_down.png) 1;
    width: 14px;
    height: 14px;
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

