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

    def __repr__(self):
	return "<SohoHookManager ({} hooks)>".format(len(self.hooks))

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def hooks(self):
	return self._hooks

    # =========================================================================

    def callHook(self, name, *args, **kwargs):
	"""Call all hook functions for a given soho hook name."""
	from IFDapi import ray_comment

	hooks = self.hooks.get(name, ())

	for hook in hooks:
	    try:
		result = hook(*args, **kwargs)

	    except Exception as e:
		ray_comment(
		    "Hook Error[{}]: {1}".format(name, str(e))
		)

		ray_comment(
		    "Traceback:\n# {}\n".format(
			    "\n#".join(traceback.format_exc().split('\n'))
		    )
		)

	    else:
		if result:
		    return True

	return False

    def registerHook(self, name, hook):
	"""Register a hook function for a given soho hook name."""
	hooks = self.hooks.setdefault(name, [])

	hooks.append(hook)

# =============================================================================
# FUNCTIONS
# =============================================================================

def getManager():
    """Get the shared hook manager."""
    return _HOOK_MANAGER

# =============================================================================

_HOOK_MANAGER = SohoHookManager()

