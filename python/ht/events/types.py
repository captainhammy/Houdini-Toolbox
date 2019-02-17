"""This module contains enums for event names."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from enum import Enum

# =============================================================================
# CLASSES
# =============================================================================

class NodeEvents(Enum):
    """Events related to node changes.  These correspond to node based event handler scripts.

    """
    OnCreated = "OnCreated"
    OnDeleted = "OnDeleted"
    OnInputChanged = "OnInputChanged"
    OnLoaded = "OnLoaded"
    OnNameChanged = "OnNameChanged"
    OnUpdated = "OnUpdated"
    PostLastDelete = "PostLastDelete"
    PreFirstCreate = "PreFirstCreate"
    SyncNodeVersion = "SyncNodeVersion"


class RopEvents(Enum):
    """Events related to ROP render event scripts."""
    PostFrame = "postframe"
    PostRender = "postrender"
    PostWrite = "postwrite"
    PreFrame = "preframe"
    PreRender = "prerender"


class SceneEvents(Enum):
    """Events related to scene events."""

    EmptyScene = "launcheemptyscene"  # 123.[cmd|py]
    # Only run when 123 gets run, after LoadPost but before FinalLoad.
    EmptyScenePostLoad = "emptyscenepostload"
    Exit = "scenequit"  # Python atexit callback
    Load = "sceneload"  # 456/[cmd|py]
    PostSave = "afterscenesave"
    PreSave = "beforesenesave"
    # When the UI first appears and Houdini begins running the UI loop
    WhenUIAvailable = "uiavailable"
    ExternalDragDrop = "externaldragdrop"
