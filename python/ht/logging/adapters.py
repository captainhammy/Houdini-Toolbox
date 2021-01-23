"""Custom logging adapters."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from contextlib import contextmanager
import logging

# Third Party Imports
# TODO: REMOVE THIS?
from logquacious.backport_configurable_stacklevel import patch_logger

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

    def __init__(self, base_logger, dialog=False, node=None, status_bar=False):
        super().__init__(base_logger, {})

        self._dialog = dialog
        self._node = node
        self._status_bar = status_bar

    # --------------------------------------------------------------------------
    # CLASS METHODS
    # --------------------------------------------------------------------------

    @classmethod
    def from_name(cls, name, dialog=False, node=None, status_bar=False):
        """Create a new HoudiniLoggerAdapter from a name.

        This is a convenience function around the following code:

        >>> base_logger = logging.getLogger(name)
        >>> logger = HoudiniLoggerAdapter(base_logger)

        :param name: The name of the logger to use.
        :type name: str
        :param dialog: Whether to always utilize the dialog option.
        :type dialog: bool
        :param node: Optional node for prefixing messages with the path.
        :type node: hou.Node
        :param status_bar: Whether to always utilize the dialog option.
        :type status_bar: bool
        :return: An adapter wrapping a logger of the passed name.
        :rtype: HoudiniLoggerAdapter

        """
        # Create a base logger
        base_logger = logging.getLogger(name)

        return cls(base_logger, dialog=dialog, node=node, status_bar=status_bar)

    # --------------------------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------------------------

    @property
    def dialog(self):
        """bool: Whether or not the dialog will be displayed."""
        return self._dialog

    @dialog.setter
    def dialog(self, dialog):
        self._dialog = dialog

    # --------------------------------------------------------------------------

    @property
    def node(self):
        """hou.Node or None: A node the logger is associated with."""
        return self._node

    @node.setter
    def node(self, node):
        self._node = node

    # --------------------------------------------------------------------------

    @property
    def status_bar(self):
        """bool: Whether or not the message will be logged to the status bar."""
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
            extra = kwargs["extra"]

            node = extra.pop("node", self.node)

            # Prepend the message with the node path.
            if node is not None:
                path = node.path()
                msg = "{} - {}".format(path, msg)

            dialog = extra.pop("dialog", self.dialog)
            status_bar = extra.pop("status_bar", self.status_bar)

            severity = hou.severityType.Message

            if hou.isUIAvailable():
                # Copy of the message for our display.
                houdini_message = msg

                # If we have message args we need to format the message with them.
                if "message_args" in extra:
                    houdini_message = houdini_message % extra["message_args"]

                severity = extra.pop("severity", severity)

                # Display the message as a popup.
                if dialog:
                    title = extra.pop("title", None)

                    hou.ui.displayMessage(
                        houdini_message, severity=severity, title=title
                    )

                if status_bar:
                    hou.ui.setStatusMessage(houdini_message, severity=severity)

        return msg, kwargs

    def critical(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger, after adding
        contextual information from this adapter instance.

        """
        _pre_process_args(hou.severityType.Error, args, kwargs)
        msg, kwargs = self.process(msg, kwargs)

        with _patch_logger(self.logger):
            self.logger.critical(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger, after adding
        contextual information from this adapter instance.

        """
        _pre_process_args(hou.severityType.Message, args, kwargs)
        msg, kwargs = self.process(msg, kwargs)

        with _patch_logger(self.logger):
            self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger, after adding
        contextual information from this adapter instance.

        """
        _pre_process_args(hou.severityType.Error, args, kwargs)
        msg, kwargs = self.process(msg, kwargs)

        with _patch_logger(self.logger):
            self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger, after adding
        contextual information from this adapter instance.

        """
        _pre_process_args(hou.severityType.Error, args, kwargs)
        msg, kwargs = self.process(msg, kwargs)

        kwargs["exc_info"] = 1

        with _patch_logger(self.logger):
            self.logger.exception(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger, after adding
        contextual information from this adapter instance.

        """
        _pre_process_args(hou.severityType.ImportantMessage, args, kwargs)
        msg, kwargs = self.process(msg, kwargs)

        with _patch_logger(self.logger):
            self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Delegate an info call to the underlying logger, after adding
        contextual information from this adapter instance.

        """
        _pre_process_args(hou.severityType.Warning, args, kwargs)
        msg, kwargs = self.process(msg, kwargs)

        with _patch_logger(self.logger):
            self.logger.warning(msg, *args, **kwargs)


# ==============================================================================
# NON-PUBLIC FUNCTIONS
# ==============================================================================


@contextmanager
def _patch_logger(logger):
    """Patch the __class__ of the logger for the duration so we can utilize the
    'stacklevel' arg.

    :param logger: The logger to patch.
    :type logger: logging.Logger
    :return:

    """
    original_logger_class = logger.__class__

    logger.__class__ = patch_logger(logger.__class__)

    try:
        yield

    finally:
        logger.__class__ = original_logger_class


def _pre_process_args(severity, args, kwargs):
    """Pre-process args.

    :param severity: The message severity.
    :type severity: hou.severityType
    :param args: The list of message args.
    :type args: tuple(str)
    :param kwargs: The kwargs dict.
    :type kwargs: dict
    :return:

    """
    extra = kwargs.setdefault("extra", {})

    # Set the severity to our passed in value.
    extra["severity"] = severity

    # Check if notify is set.
    if "notify_send" in kwargs:
        extra["notify_send"] = kwargs.pop("notify_send")

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

    # Stash any log format args so we can pass them along to process().
    if args:
        extra["message_args"] = args

    if "stacklevel" not in kwargs:
        # Set stacklevel=2 so that the module/file/line reporting will represent
        # the calling point and not the function call inside the adapter..
        kwargs["stacklevel"] = 2
