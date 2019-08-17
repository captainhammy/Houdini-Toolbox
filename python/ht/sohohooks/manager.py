"""This module provides functionality for manager soho hooks."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import traceback


# =============================================================================
# CLASSES
# =============================================================================

class SohoHookManager(object):
    """This class manages custom soho hooks."""

    def __init__(self):
        self._hooks = {}

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<SohoHookManager ({} hooks)>".format(len(self.hooks))

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def hooks(self):
        """Dictionary of hook functions grouped by hook name."""
        return self._hooks

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def call_hook(self, name, *args, **kwargs):
        """Call all hook functions for a given soho hook name.

        :param name: The name of the hook to call.
        :type name: str
        :return: Whether or not the hooks succeeded.
        :rtypeL bool

        """
        from IFDapi import ray_comment

        # Get a list of hooks to call.
        hooks = self.hooks.get(name, ())

        return_value = False

        for hook in hooks:
            try:
                result = hook(*args, **kwargs)

            # Catch any exceptions and 'log' them to the ifd via comments.
            except Exception as e:
                ray_comment(
                    "Hook Error[{}]: {}".format(name, str(e))
                )

                ray_comment(
                    "Traceback:\n# {}\n".format(
                        "\n#".join(traceback.format_exc().split('\n'))
                    )
                )

            else:
                if result:
                    return_value = True

        return return_value

    def register_hook(self, name, hook):
        """Register a hook function for a given soho hook name.

        :param name: The hook name.
        :type name: str
        :param hook: The function to call.
        :type hook: function
        :return:

        """
        hooks = self.hooks.setdefault(name, [])

        hooks.append(hook)


# =============================================================================

MANAGER = SohoHookManager()
