"""Custom logging adapters."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Future
from __future__ import annotations

# Standard Library
import logging
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

# Houdini
import hou


# ==============================================================================
# GLOBALS
# ==============================================================================

# Call kwargs that should be moved into the extra data passed to process().
_KWARGS_TO_EXTRA_KEYS = (
    "node",
    "dialog",
    "status_bar",
    "title",
)

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


# ==============================================================================
# CLASSES
# ==============================================================================


class HoudiniLoggerAdapter(logging.LoggerAdapter):
    """Custom LoggerAdapter for Houdini that allows automated addition of node
    paths and log display in dialogs, status bar, etc.  Also allows for
    automated notification.

    :param base_logger: The base package logger.
    :param node: Optional node for prefixing messages with the path.
    :param dialog: Whether to always utilize the dialog option.
    :param status_bar: Whether to always utilize the dialog option.
    :param extra: Extra args to use to generate log messages.
    """

    def __init__(
        self,
        base_logger: logging.Logger,
        node: hou.Node = None,
        dialog: bool = False,
        status_bar: bool = False,
        extra: Optional[dict] = None,
    ) -> None:
        extra = extra if extra else {}

        super().__init__(base_logger, extra)

        self._dialog = dialog
        self._node = node
        self._status_bar = status_bar

    def __new__(
        cls: Type[HoudiniLoggerAdapter], *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> HoudiniLoggerAdapter:  # pragma: no cover
        """Overridden __new__ that will wrap logging methods with custom function."""
        inst = super(HoudiniLoggerAdapter, cls).__new__(cls)

        # We want to wrap various log calls to process args and set severities.
        for key, severity in _TO_WRAP.items():
            if hasattr(inst, key):
                attr = getattr(inst, key)

                if callable(attr):
                    wrapped = _wrap_logger(attr, severity)

                    setattr(inst, key, wrapped)

        return inst

    # --------------------------------------------------------------------------
    # CLASS METHODS
    # --------------------------------------------------------------------------

    @classmethod
    def from_name(
        cls,
        name: str,
        node: hou.Node = None,
        dialog: bool = False,
        status_bar: bool = False,
        extra: Optional[dict] = None,
    ) -> HoudiniLoggerAdapter:
        """Create a new HoudiniLoggerAdapter from a name.

        This is a convenience function around the following code:

        >>> base_log = logging.getLogger(name)
        >>> logger = HoudiniLoggerAdapter(base_log)

        :param name: The name of the logger to use.
        :param dialog: Whether to always utilize the dialog option.
        :param node: Optional node for prefixing messages with the path.
        :param status_bar: Whether to always utilize the dialog option.
        :param extra: Extra args to use to generate log messages.
        :return: An adapter wrapping a logger of the passed name.

        """
        # Create a base logger
        base_logger = logging.getLogger(name)

        return cls(base_logger, node=node, dialog=dialog, status_bar=status_bar, extra=extra)

    # --------------------------------------------------------------------------
    # PROPERTIES
    # --------------------------------------------------------------------------

    @property
    def dialog(self) -> bool:
        """Whether the dialog will be displayed."""
        return self._dialog

    @dialog.setter
    def dialog(self, dialog: bool) -> None:
        self._dialog = dialog

    # --------------------------------------------------------------------------

    @property
    def node(self) -> Optional[hou.Node]:
        """A node the logger is associated with."""
        return self._node

    @node.setter
    def node(self, node: Optional[hou.Node]) -> None:
        self._node = node

    # --------------------------------------------------------------------------

    @property
    def status_bar(self) -> bool:
        """Whether the message will be logged to the status bar."""
        return self._status_bar

    @status_bar.setter
    def status_bar(self, status_bar: bool) -> None:
        self._status_bar = status_bar

    # --------------------------------------------------------------------------
    # METHODS
    # --------------------------------------------------------------------------

    def process(self, msg: str, kwargs: Any) -> Tuple[str, Any]:
        """Override process() function to possibly insert a node path or to
        display a dialog with the log message before being passed to regular
        logging output.

        :param msg: The log message.
        :param kwargs: kwargs dict.
        :return: The message and updated kwargs.

        """
        extra: dict = self.extra  # type: ignore

        if "extra" in kwargs:
            extra.update(kwargs["extra"])

            node = extra.pop("node", self.node)

            # Prepend the message with the node path.
            if node is not None:
                msg = f"{node.path()} - {msg}"

            dialog = extra.pop("dialog", self.dialog)
            status_bar = extra.pop("status_bar", self.status_bar)

            if hou.isUIAvailable():
                # Copy of the message for our display.
                houdini_message = msg

                # If we have message args we need to format the message with them.
                if "message_args" in extra:
                    houdini_message = houdini_message % extra["message_args"]

                severity = extra.pop("severity", hou.severityType.Message)

                # Display the message as a popup.
                if dialog:
                    title = extra.pop("title", None)

                    hou.ui.displayMessage(
                        houdini_message, severity=severity, title=title
                    )

                if status_bar:
                    hou.ui.setStatusMessage(houdini_message, severity=severity)

        kwargs["extra"] = extra

        return msg, kwargs


# ==============================================================================
# NON-PUBLIC FUNCTIONS
# ==============================================================================



def _wrap_logger(func: Callable, severity: hou.severityType) -> Callable:
    """Function which wraps a logger method with custom code."""

    @wraps(func)
    def func_wrapper(*args: Any, **kwargs: Any) -> Any:  # pylint: disable=missing-docstring
        # Get the extra dictionary or an empty one if it doesn't exist.
        extra = kwargs.setdefault("extra", {})

        # Set the severity to our passed in value.
        extra["severity"] = severity

        for key in _KWARGS_TO_EXTRA_KEYS:
            if key in kwargs:
                extra[key] = kwargs.pop(key)

        # If there is more than one arg we want to pass them as extra data so that
        # we can use it to format the message for extra outputs.
        if len(args) > 1:
            extra["message_args"] = args[1:]

        if "stacklevel" not in kwargs:
            # Set stacklevel=4 so that the module/file/line reporting will represent
            # the calling point and not the function call inside the adapter.
            kwargs["stacklevel"] = 4

        return func(*args, **kwargs)

    return func_wrapper
