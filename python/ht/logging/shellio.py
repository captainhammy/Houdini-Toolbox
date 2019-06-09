"""Custom logging stream handler which writes to Houdini Python Shell panels."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import logging
import sys

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

class PythonShellHandler(logging.StreamHandler):
    """Custom stream handler which outputs to the interactive Python shell
    when it is open.

    Houdini will redirect sys.stdout to be an instance of hou.ShellIO when there
    is a Python Shell panel active and displayed.  This handler works by checking
    that sys.stdout is a hou.ShellIO and writes output to it accordingly.  If
    it is not, no output will be written.

    """

    def emit(self, record):
        try:
            msg = self.format(record)

            stream = sys.stdout

            if isinstance(stream, hou.ShellIO):
                stream.write(msg)
                stream.write('\n')
                stream.flush()

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception:
            self.handleError(record)
