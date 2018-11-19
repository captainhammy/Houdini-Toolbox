"""This module contains an operation to set the primary image path."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter
from ht.pyfilter.property import set_property

# =============================================================================
# CLASSES
# =============================================================================

class SetPrimaryImage(PyFilterOperation):
    """Operation to modify the primary image path.

    """

    def __init__(self, manager):
        super(SetPrimaryImage, self).__init__(manager)

        self._disable_primary_image = False
        self._primary_image_path = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def disable_primary_image(self):
        """bool: Disable primary image generation."""
        return self._disable_primary_image

    @disable_primary_image.setter
    def disable_primary_image(self, disable_primary_image):
        self._disable_primary_image = disable_primary_image

    @property
    def primary_image_path(self):
        """str: The primary image path to set."""
        return self._primary_image_path

    @primary_image_path.setter
    def primary_image_path(self, primary_image_path):
        self._primary_image_path = primary_image_path

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def build_arg_string(primary_image_path=None, disable_primary_image=False):
        """Build an argument string for this operation."""
        args = []

        if primary_image_path is not None:
            args.append("--primary-image-path={}".format(primary_image_path))

        if disable_primary_image:
            args.append("--disable-primary-image")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation."""
        parser.add_argument("--primary-image-path", dest="primary_image_path")

        parser.add_argument(
            "--disable-primary-image",
            action="store_true",
            dest="disable_primary_image"
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @log_filter
    def filterCamera(self):
        """Apply camera properties."""
        if self.disable_primary_image:
            logger.info("Disabling primary image")
            set_property("image:filename", "null:")

        elif self.primary_image_path is not None:
            set_property("image:filename", self.primary_image_path)

    def process_parsed_args(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.disable_primary_image:
            self.disable_primary_image = True

        if filter_args.primary_image_path is not None:
            self.primary_image_path = filter_args.primary_image_path

    def should_run(self):
        """Run if the operation is disabling the primary image or needs to set
        the image path.

        """
        return self.disable_primary_image or self.primary_image_path is not None
