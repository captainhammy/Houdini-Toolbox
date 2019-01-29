"""This module contains an event to perform actions on scene load."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events.item import HoudiniEventItem
from ht.events.types import NodeEvents, SceneEvents

from ht.logger import logger

from ht.sohohooks.aovs.manager import MANAGER
from ht.sohohooks.aovs.sources import AOVAssetSectionSource, AOVHipSource

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class AOVEvents(HoudiniEventGroup):
    """Event to run on scene load (456)."""

    def __init__(self):
        super(AOVEvents, self).__init__()

        self.event_map.update(
            {
                NodeEvents.OnLoaded: HoudiniEventItem((self.load_embedded_aovs,)),
                SceneEvents.Load: HoudiniEventItem((self.load_hip_aovs,))
            }
        )

    # =========================================================================
    # METHODS
    # =========================================================================)

    def load_embedded_aovs(self, scriptargs):
        """Load any AOVs that are contained in the hip file being opened."""
        node_type = scriptargs["type"]

        definition = node_type.definition()

        if definition is not None:
            sections = definition.sections()

            if AOVAssetSectionSource.SECTION_NAME in sections:
                logger.info("load asset section aovs")

                section = sections[AOVAssetSectionSource.SECTION_NAME]

                aov_asset = AOVAssetSectionSource(section)

                MANAGER.load_source(aov_asset)

    def load_hip_aovs(self, scriptargs):
        """Load any AOVs that are contained in the hip file being opened."""
        root = hou.node("/")

        hip_source = MANAGER.source_manager.get_hip_source()

        if hip_source is None:
            hip_source = MANAGER.source_manager.init_hip_source()

        else:
            hip_source.clear()

        if AOVHipSource.USER_DATA_NAME in root.userDataDict():
            logger.info("load hip aovs")
            MANAGER.load_source(hip_source)

        unsaved_source = MANAGER.source_manager.get_unsaved_source()
        unsaved_source.clear()
