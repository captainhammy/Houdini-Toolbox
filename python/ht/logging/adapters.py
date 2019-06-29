"""Custom logging adapters."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Python Imports
from __future__ import absolute_import

from functools import wraps
import logging

# Houdini Imports
import hou


# ==============================================================================
# CLASSES
# ==============================================================================

class HoudiniLoggerAdapter(logging.LoggerAdapter):
    """Custom LoggerAdapter for Houdini that allows automated addition of node
    paths and log display in dialogs, status bar, etc.  Also allows for
    automated notification.

    :param base_logger: The base package logger.
    :type base_logger: logging.Logger
    :param dialog: Whether to always utilize the dialog option.
    :type dialog: bool
    :param node: Optional node for prefixing messages with the path.
    :type node: hou.Node
    :param status_bar: Whether to always utilize the dialog option.
    :type status_bar: bool

    """

    # Logging functions to wrap, and a corresponding severity for popup
    # messages.
    _TO_WRAP = {
        "critical": hou.severityType.Error,
        "debug": hou.severityType.Message,
        "error": hou.severityType.Error,
        "exception": hou.severityType.Error,
        "info": hou.severityType.ImportantMessage,
        "warning": hou.severityType.Warning,
    }

    def __init__(self, base_logger, dialog=False, node=None, status_bar=False):
        super(HoudiniLoggerAdapter, self).__init__(base_logger, {})

        self._dialog = dialog
        self._node = node
        self._status_bar = status_bar

    # --------------------------------------------------------------------------
    # SPECIAL METHODS
    # --------------------------------------------------------------------------

    def __new__(cls, *args, **kwargs):
        # We want to wrap various log calls to process args and set severities.
        for key, severity in cls._TO_WRAP.items():
            if hasattr(cls, key):
                attr = getattr(cls, key)

                wrapped = _wrap_logger(attr, severity)

                setattr(cls, key, wrapped)

        return super(HoudiniLoggerAdapter, cls).__new__(cls, *args, **kwargs)

    # --------------------------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------------------------

    @property
    def dialog(self):
        """Whether or not the dialog will be displayed.

        :rtype: bool

        """
        return self._dialog

    @dialog.setter
    def dialog(self, dialog):
        self._dialog = dialog

    # --------------------------------------------------------------------------

    @property
    def node(self):
        """A node the logger is associated with.

        :rtype: hou.Node or None

        """
        return self._node

    @node.setter
    def node(self, node):
        self._node = node

    # --------------------------------------------------------------------------

    @property
    def status_bar(self):
        """Whether or not the message will be logged to the status bar.

        :rtype: bool

        """
        return self._status_bar

    @status_bar.setter
    def status_bar(self, status_bar):
        self._status_bar = status_bar

    # --------------------------------------------------------------------------
    # METHODS
    # --------------------------------------------------------------------------

    def process(self, msg, kwargs):
        """Override process() function to possibly insert a node path or to
        display a dialog with the log message before being passed to regular
        logging output.

        :param msg: The log message.
        :type msg: str
        :param kwargs: kwargs dict.
        :type kwargs: dict
        :return: The message and updated kwargs.
        :rtype: (str, dict)

        """
        if "extra" in kwargs:
            data = kwargs["extra"]

            node = data.pop("node", self.node)

            # Prepend the message with the node path.
            if node is not None:
                path = node.path()
                msg = "{} - {}".format(path, msg)

            dialog = data.pop("dialog", self.dialog)
            status_bar = data.get("status_bar", self.status_bar)

            severity = hou.severityType.Message

            if hou.isUIAvailable():
                # Display the message as a popup.
                if dialog:
                    severity = data.pop("severity", severity)
                    title = data.pop("title", None)

                    hou.ui.displayMessage(msg, severity=severity, title=title)

                if status_bar:
                    severity = data.pop("severity", severity)

                    hou.ui.setStatusMessage(msg, severity=severity)

        return msg, kwargs


# ==============================================================================
# NON-PUBLIC FUNCTIONS
# ==============================================================================

def _wrap_logger(func, severity):
    """Function which wraps a logger method with custom code."""

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        # Get the extra dictionary or an empty one if it doesn't exist.
        extra = kwargs.setdefault("extra", {})

        # Set the severity to our passed in value.
        extra["severity"] = severity

        # If a 'node' arg was passed to the call, remove it and store the
        # node.
        if "node" in kwargs:
            extra["node"] = kwargs.pop("node")

        # If a 'dialog' arg was passed to the call, remove it and store the
        # value.
        if "dialog" in kwargs:
            extra["dialog"] = kwargs.pop("dialog")

        # If a 'status_bar' arg was passed to the call, remove it and store the
        # value.
        if "status_bar" in kwargs:
            extra["status_bar"] = kwargs.pop("status_bar")

        # If a 'title' arg was passed to the call, remove it and store the
        # value.
        if "title" in kwargs:
            extra["title"] = kwargs.pop("title")

        return func(*args, **kwargs)

    return func_wrapper
