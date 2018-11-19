"""This module contains an operation to force a zdepth pass."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter
from ht.pyfilter.property import get_property, set_property

# =============================================================================
# CLASSES
# =============================================================================

class ZDepthPass(PyFilterOperation):
    """Force the render to only contain C and Pz planes.

    As long as there is an extra image plane that is not C or Of this operation
    will remap an extra image plane to be Pz and disable the rest.

    This operation creates and uses the --zdepth arg.

    """

    CONST_SHADER = "opdef:/Shop/v_constant clr 0 0 0"

    def __init__(self, manager):
        super(ZDepthPass, self).__init__(manager)

        # Should the operation be run.
        self._active = False

        # We have not set the Pz plane yet.
        self.data["set_pz"] = False

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def active(self):
        """bool:  Is the operation active."""
        return self._active

    @active.setter
    def active(self, active):
        self._active = active

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def build_arg_string(active=False):
        args = []

        if active:
            args.append("--zdepth")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation."""
        parser.add_argument(
            "--zdepth",
            action="store_true"
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @log_filter("object:name")
    def filterInstance(self):
        """Apply constant black shader to objects."""
        matte = get_property("object:matte")
        phantom = get_property("object:phantom")
        surface = get_property("object:surface")

        set_property("object:overridedetail", True)

        if matte or phantom or surface == "matte":
            set_property("object:phantom", 1)

        else:
            set_property("object:surface", self.CONST_SHADER.split())
            set_property("object:displace", None)

    @log_filter("plane:variable")
    def filterPlane(self):
        """Modify image planes to ensure one will output Pz.

        This will disable all planes that are not C and Pz.

        """
        channel = get_property("plane:channel")

        if channel == "Pz":
            # If the channel is Pz but we've already forcibly set one to Pz
            # then we need to disable the plane.
            if self.data["set_pz"]:
                set_property("plane:disable", True)

                return

            # The plane is Pz and we have yet to indicate we've got a Pz so
            # store the data.
            else:
                self.data["set_pz"] = True

                return

        # If we haven't found a Pz plane yet and this channel isn't a primary
        # output channel then we will force it to be Pz.
        if not self.data["set_pz"] and channel not in ("C", "Of"):
            set_property("plane:variable", "Pz")
            set_property("plane:vextype", "float")
            set_property("plane:channel", "Pz")
            set_property("plane:pfilter", "minmax min")
            set_property("plane:quantize", None)
            self.data["set_pz"] = True

        # Disable any other planes.
        elif channel not in ("C", ):
            set_property("plane:disable", True)

    def process_parsed_args(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.zdepth is not None:
            self._active = filter_args.zdepth

    def should_run(self):
        """Only run if the flag was passed."""
        return self._active
