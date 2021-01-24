"""Classes for finding, copying and pasting of files."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from __future__ import annotations
import abc
import datetime
import getpass
import json
import os
import platform
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

# Houdini Toolbox Imports
from ht.ui.paste import utils
import ht.ui.paste.helpers

# Houdini Imports
import hou

if TYPE_CHECKING:
    from PySide2 import QtGui

# Handle differences between platforms.
if platform.system() == "Windows":
    _CONTEXT_SEP = "@"
    getpwuid = None

else:
    _CONTEXT_SEP = ":"
    from pwd import getpwuid


# ==============================================================================
# CLASSES
# ==============================================================================


class SourceManager:
    """Manager class for all source objects."""

    def __init__(self):
        self._sources = []

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def sources(self) -> List[CopyPasteSource]:
        """List of all available sources."""
        return self._sources


# Sources


class CopyPasteSource(abc.ABC):
    """Base class for managing copy/paste items.

    """

    def __init__(self):
        self._sources = {}

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """The source display name."""

    @property
    @abc.abstractmethod
    def icon(self) -> QtGui.QIcon:
        """The icon for the source."""

    @property
    def sources(self) -> Dict[str, List[CopyPasteItemSource]]:
        """The item sources."""
        return self._sources

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @abc.abstractmethod
    def copy_helper_widget(self) -> ht.ui.paste.helpers._BaseCopyHelperWidget:  # pylint: disable=protected-access
        """Get the copy helper widget for this source.

        :return: The helper widget to copy items to this source.

        """

    @abc.abstractmethod
    def create_source(self, *args, **kwargs):
        """Create a new source."""

    @abc.abstractmethod
    def get_sources(self, context: str) -> List[CopyPasteItemSource]:
        """Return a list of any sources for the context.

        :param context: A Houdini context name.
        :return: Available sources for the context.

        """

    @abc.abstractmethod
    def paste_helper_widget(self) -> ht.ui.paste.helpers._BasePasteHelperWidget:  # pylint: disable=protected-access
        """Get the paste helper widget for this source.

        :return: The helper widget to paste items from this source.

        """

    @abc.abstractmethod
    def refresh(self):
        """Refresh the list of sources.

        :return:

        """


class HomeDirSource(CopyPasteSource):
    """Copy/Paste .cpio items from ~/copypaste."""

    _extension = ".cpio"

    _base_path = os.path.join(os.path.expanduser("~"), "copypaste")

    def __init__(self):
        super().__init__()

        self._init_sources()

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def pack_name(name: str) -> str:
        """Take a source name and convert it to a name suitable for a file.

        This method will replace all spaces with '--'.

        :param name: The name to pack.
        :return: The packed name.

        """
        return name.replace(" ", "--")

    @staticmethod
    def unpack_name(name: str) -> str:
        """Unpack a file name into a source name.

        This method will replace all '--' with spaces.

        :param name: The name to unpack.
        :return: The unpacked name.

        """
        return name.replace("--", " ")

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _create_sidecar_file(self, base_path: str, data: dict) -> str:
        """Write a .json sidecar file with the item info.

        :param base_path: The path of the main file.
        :param data: The data to write.
        :return: The sidecar file path.

        """
        sidecar_path = base_path.replace(self._extension, ".json")

        with open(sidecar_path, "w") as handle:
            json.dump(data, handle, indent=4)

        return sidecar_path

    def _init_sources(self):
        """Initialize all the source items.

        :return:

        """
        # The target folder might not exist if nothing has been copied for that
        # context.
        if not os.path.exists(self._base_path):
            return

        files = os.listdir(self._base_path)

        for file_name in files:
            if os.path.splitext(file_name)[1] == self._extension:
                path = os.path.join(self._base_path, file_name)

                item = CPIOContextCopyPasteItemFile.from_path(path)

                if item is not None:
                    context_sources = self.sources.setdefault(item.context, [])
                    context_sources.append(item)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        """A display name for this source."""
        return "$HOME"

    @property
    def icon(self) -> QtGui.QIcon:
        """The icon for the source."""
        return hou.qt.createIcon("MISC_satchel")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def copy_helper_widget(self, *args, **kwargs) -> ht.ui.paste.helpers.HomeToolDirItemsCopyHelperWidget:  # pylint: disable=arguments-differ
        """Get the copy helper widget for this source.

        :return: The helper widget to copy items to this source.

        """
        return ht.ui.paste.helpers.HomeToolDirItemsCopyHelperWidget(
            self, *args, **kwargs
        )

    def create_source(  # pylint: disable=arguments-differ
        self, context: str, name: str, description: Optional[str]=None
    ) -> CPIOContextCopyPasteItemFile:
        """Create a new item source.

        :param context: The operator context of the source.
        :param name: The name of the source.
        :param description: Optional description of the source.
        :return: The created source item.

        """
        clean_name = self.pack_name(name)

        # The file name consists of the user name and the description, separated
        # by a :.
        file_name = "{}{}{}{}".format(
            context, _CONTEXT_SEP, clean_name, self._extension
        )

        file_path = os.path.join(self._base_path, file_name)

        sidecar_data = {
            "author": getpass.getuser(),
            "name": name,
            "context": context,
            "date": ht.ui.paste.utils.date_to_string(datetime.datetime.now()),
        }

        if description is not None:
            sidecar_data["description"] = description

        sidecar_path = self._create_sidecar_file(file_path, sidecar_data)

        source = CPIOContextCopyPasteItemFile(file_path, context, name, sidecar_path)

        context_sources = self.sources.setdefault(context, [])
        context_sources.append(source)

        return source

    def destroy_item(self, item: CopyPasteItemSource):
        """Destroy and item and remove it from the source map.

        :param item: The item to remove and destroy.
        :return:

        """
        context_sources = self.sources.get(item.context, {})

        if item in context_sources:
            item.destroy()
            context_sources.remove(item)

    def get_sources(self, context: str) -> List[CopyPasteItemSource]:
        """Get a list of available sources for a context.

        :param context: An operator context name.
        :return: Available sources for the context.


        """
        return self.sources.get(context, [])

    def paste_helper_widget(self, *args, **kwargs) -> ht.ui.paste.helpers.HomeToolDirItemsPasteHelperWidget:  # pylint: disable=arguments-differ
        """Get the paste helper widget for this source.

        :return: The helper widget to paste items from this source.

        """
        return ht.ui.paste.helpers.HomeToolDirItemsPasteHelperWidget(
            self, *args, **kwargs
        )

    def refresh(self):
        """Refresh the internal sources.

        This will clear the internal data and reload all sources.

        :return:

        """
        self.sources.clear()

        self._init_sources()


# Item Sources


class CopyPasteItemSource(abc.ABC):
    """Class responsible for loading and saving items from a source.

    :param context: The operator context.

    """

    def __init__(self, context: str):
        self._context = context

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    @abc.abstractmethod
    def author(self) -> str:
        """The name of the item author."""

    @property
    def context(self) -> str:
        """The operator context name."""
        return self._context

    @property
    @abc.abstractmethod
    def date(self) -> datetime.datetime:
        """datetime.datetime: The date of creation."""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """The item description."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The item name."""

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @abc.abstractmethod
    def destroy(self):
        """Remove this item and all associated files.

        :return:

        """

    @abc.abstractmethod
    def load_items(self, parent: hou.Node):
        """Load this source's items under the parent node.

        :param parent: The node to load the items under.

        """

    @abc.abstractmethod
    def save_items(self, parent: hou.Node, items: Tuple[hou.NetworkItem]):
        """Save the supplied items under the parent node..

        :param parent: The parent node of the items to save.
        :param items: The items to save.
        :return:

        """


class CPIOContextCopyPasteItemFile(CopyPasteItemSource):
    """Class to load and save items from .cpio files.

    :param file_path: The path to the file.
    :param context: The operator context.
    :param name: The item name.
    :param sidecar_path: Optional path to a sidecar file.

    """

    _extension = ".cpio"

    def __init__(self, file_path: str, context: str, name: str, sidecar_path: Optional[str] = None):
        super().__init__(context)

        self._author = None
        self._date = None
        self._description = None
        self._file_path = file_path
        self._name = name
        self._sidecar_path = sidecar_path

        self._init_metadata()

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.file_path)

    # -------------------------------------------------------------------------
    # CLASS METHODS
    # -------------------------------------------------------------------------

    @classmethod
    def from_path(cls, file_path: str) -> CPIOContextCopyPasteItemFile:
        """Initialize a new object based on a file path.

        :param file_path: The path to the source file.
        :return: A new object based on the file path.

        """
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        context, name = file_name.split(_CONTEXT_SEP)

        name = cls.unpack_name(name)

        return cls(file_path, context, name)

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def pack_name(name: str) -> str:
        """Take a source name and convert it to a name suitable for a file.

        This method will replace all spaces with '--'.

        :param name: The name to pack.
        :return: The packed name.

        """
        return name.replace(" ", "--")

    @staticmethod
    def unpack_name(name: str) -> str:
        """Unpack a file name into a source name.

        This method will replace all '--' with spaces.

        :param name: The name to unpack.
        :return: The unpacked name.

        """
        return name.replace("--", " ")

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _init_metadata(self):
        """Initialize data based on the sidecar file.

        :return:

        """
        # No sidecar path so assume the default one.
        if self._sidecar_path is None:
            self._sidecar_path = self.file_path.replace(self._extension, ".json")

        # If the file exists, read it.
        if os.path.exists(self._sidecar_path):
            with open(self._sidecar_path) as handle:
                sidecar_data = json.load(handle)

        else:
            sidecar_data = None

        # If data was found then set various properties based on it.
        if sidecar_data is not None:
            self._author = sidecar_data.get("author")

            date = sidecar_data.get("date")
            self._date = utils.date_from_string(date)

            description = sidecar_data.get("description")

            if description is not None:
                self._description = description

        # Need to stat file for info.
        else:
            stat_data = os.stat(self.file_path)

            if getpwuid is not None:
                self._author = getpwuid(stat_data.st_uid).pw_name

            else:
                self._author = "unknown"

            self._date = datetime.datetime.fromtimestamp(stat_data.st_mtime)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @property
    def author(self) -> str:
        """The name of the item author."""
        return self._author

    @property
    def date(self) -> datetime.datetime:
        """The date of creation."""
        return self._date

    @property
    def description(self) -> str:
        """The item description."""
        return self._description

    @property
    def file_path(self) -> str:
        """The path to the source file."""
        return self._file_path

    @property
    def name(self) -> str:
        """The item name."""
        return self._name

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def destroy(self):
        """Remove this item and all associated files.

        :return:

        """
        if self._sidecar_path is not None:
            if os.path.exists(self._sidecar_path):
                os.remove(self._sidecar_path)

        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def load_items(self, parent: hou.Node):
        """Load this source's items under the parent node.

        :param parent: The node to load the items under.

        """
        parent.loadItemsFromFile(self.file_path)

    def save_items(self, parent: hou.Node, items: Tuple[hou.NetworkItem]):
        """Save the supplied items under the parent node..

        :param parent: The parent node of the items to save.
        :param items: The items to save.
        :return:

        """
        target_folder = os.path.dirname(self.file_path)

        # Ensure the path exists.
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)

        parent.saveItemsToFile(items, self.file_path)
