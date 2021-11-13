"""This module provides functionality for manager soho hooks."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import traceback
from typing import Callable

# =============================================================================
# CLASSES
# =============================================================================


class SohoHookManager:
    """This class manages custom soho hooks."""

    def __init__(self):
        self._hooks = {}

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return f"<SohoHookManager ({len(self.hooks)} hooks)>"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def hooks(self) -> dict:
        """Dictionary of hook functions grouped by hook name."""
        return self._hooks

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def call_hook(self, name: str, *args, **kwargs) -> bool:
        """Call all hook functions for a given soho hook name.

        :param name: The name of the hook to call.
        :return: Whether or not the hooks succeeded.

        """
        from IFDapi import ray_comment

        # Get a list of hooks to call.
        hooks = self.hooks.get(name, ())

        return_value = False

        for hook in hooks:
            try:
                result = hook(*args, **kwargs)

            # Catch any exceptions and 'log' them to the ifd via comments.
            except Exception as inst:  # pylint: disable=broad-except
                ray_comment(f"Hook Error[{name}]: {inst}")

                msg = "\n#".join(traceback.format_exc().split("\n"))
                ray_comment(f"Traceback:\n# {msg}\n")

            else:
                if result:
                    return_value = True

        return return_value

    def register_hook(self, name: str, hook: Callable):
        """Register a hook function for a given soho hook name.

        :param name: The hook name.
        :param hook: The function to call.
        :return:

        """
        hooks = self.hooks.setdefault(name, [])

        hooks.append(hook)


# =============================================================================

HOOK_MANAGER = SohoHookManager()
