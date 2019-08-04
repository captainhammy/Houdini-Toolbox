"""This module contains an event to perform actions on scene load."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import logging

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events.item import HoudiniEventItem
from ht.events.types import HipFileEvents, NodeEvents

from ht.sohohooks.aovs.manager import MANAGER
from ht.sohohooks.aovs.sources import AOVAssetSectionSource

_logger = logging.getLogger(__name__)

# =============================================================================
# CLASSES
# =============================================================================

class AOVEvents(HoudiniEventGroup):
    """Event to run on scene load (456)."""

    def __init__(self):
        super(AOVEvents, self).__init__()

        self.event_map.update(
            {
                NodeEvents.OnInstall: HoudiniEventItem((self.load_embedded_aovs,)),
                NodeEvents.OnUninstall: HoudiniEventItem((self.unload_embedded_aovs,)),
                HipFileEvents.AfterLoad: HoudiniEventItem((self.load_hip_aovs,)),
                HipFileEvents.BeforeClear: HoudiniEventItem((self.unload_hip_aovs,))
            }
        )

    # =========================================================================
    # METHODS
    # =========================================================================)

    def load_embedded_aovs(self, scriptargs):
        """Load any AOVs that are contained in the hip file being opened."""
        node_type = scriptargs["type"]

        section = _get_aov_section_from_node_type(node_type)

        if section is not None:
            _logger.info("load asset section aovs: %s/%s", node_type.name(), section.name())
            MANAGER.load_section_source(section)

    def load_hip_aovs(self, scriptargs):
        """Load any AOVs that are contained in the hip file being opened."""
        MANAGER.init_hip_source()

    def unload_embedded_aovs(self, scriptargs):
        """Unload any AOVs that are contained in the hip file being opened."""
        node_type = scriptargs["type"]

        section = _get_aov_section_from_node_type(node_type)

        if section is not None:
            _logger.info("unload asset section aovs: %s/%s", node_type.name(), section.name())
            MANAGER.remove_section_source(section)

    def unload_hip_aovs(self, scriptargs):
        """Unload any AOVs that are contained in the hip file being opened."""
        MANAGER.clear_hip_source()


def _get_aov_section_from_node_type(node_type):
    definition = node_type.definition()

    section = None

    if definition is not None:
        sections = definition.sections()

        if AOVAssetSectionSource.SECTION_NAME in sections:
            section = sections[AOVAssetSectionSource.SECTION_NAME]

    return section
