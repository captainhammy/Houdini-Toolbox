"""Classes for finding, copying and pasting of files."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
import abc
import datetime
import getpass
import json
import os
from pwd import getpwuid
import re

# Houdini Toolbox Imports
from ht.ui.paste import utils
import ht.ui.paste.widgets



# Houdini Imports
import hou

# ==============================================================================
# CLASSES
# ==============================================================================

class SourceManager(object):
    """Manager class for all source objects."""

    def __init__(self):
        self._sources = []

    @property
    def sources(self):
        return self._sources


class CopyPasteSource(object):
    """Base class for managing copy/paste items"""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._sources = {}

    @abc.abstractproperty
    def display_name(self):
        pass

    @abc.abstractproperty
    def icon(self):
        pass

    @property
    def sources(self):
        return self._sources

    @abc.abstractmethod
    def create_source(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_sources(self, context):
        pass

    @abc.abstractmethod
    def copy_helper_widget(self):
        pass

    @abc.abstractmethod
    def paste_helper_widget(self):
        pass

    @abc.abstractmethod
    def refresh(self):
        pass


class CPIOHierarchicalUserFileCopyPasteSource(CopyPasteSource):
    """Class responsible for handling .cpio file sources arranged in context folders."""

    def __init__(self):
        super(CPIOHierarchicalUserFileCopyPasteSource, self).__init__()

        if self._base_path is None:
            return

        # The target folder might not exist if nothing has been copied for that
        # context.
        if not os.path.exists(self._base_path):
            return

        contexts = os.listdir(self._base_path)

        for context in contexts:
            context_path = os.path.join(self._base_path, context)

            files = os.listdir(context_path)

            context_sources = self.sources.setdefault(context, [])

            for p in files:
                if re.match("\w+:[\w_-]+\.cpio", p) is not None:
                    context_sources.append(CPIOAuthoredCopyPasteItemFile(context, os.path.join(context_path, p)))

    def create_source(self, context, description, author=None, base_path=None):
        if author is None:
            author = getpass.getuser()

        if base_path is None:
            base_path = self._base_path

        clean_description = description.replace(" ", "-")

        # The file name consists of the user name and the description, separated
        # by a :.
        file_name = "{}:{}.cpio".format(author, clean_description)

        file_path = os.path.join(base_path, context, file_name)

        source = CPIOAuthoredCopyPasteItemFile(context, file_path)

        context_sources = self.sources.setdefault(context, [])
        context_sources.append(source)

        return source

    def get_sources(self, context):
        return self.sources.get(context, [])

    def copy_helper_widget(self, *args, **kwargs):
        return ht.ui.paste.widgets.BaseCopyHelperWidget(self, *args, **kwargs)

    def paste_helper_widget(self, *args, **kwargs):
        return ht.ui.paste.widgets.DirectoryItemsPasteHelperWidget(self, *args, **kwargs)


class HomeToolDirSource(CopyPasteSource):
    """Copy/Paste .cpio items from ~/tooldev/copypaste."""

    _extension = ".cpio"

    _base_path = os.path.join(os.path.expanduser("~"), "tooldev", "copypaste")

    def __init__(self):
        super(HomeToolDirSource, self).__init__()

        self._init_sources()

    def _init_sources(self):
        # The target folder might not exist if nothing has been copied for that
        # context.
        if not os.path.exists(self._base_path):
            return

        files = os.listdir(self._base_path)

        for p in files:

            if os.path.splitext(p)[1] == self._extension:
                path = os.path.join(self._base_path, p)

                item = CPIOContextCopyPasteItemFile.from_path(path)

                if item is not None:
                    context_sources = self.sources.setdefault(item.context, [])
                    context_sources.append(item)


    @property
    def display_name(self):
        return "~/tooldev"

    @property
    def icon(self):
        return hou.qt.createIcon("MISC_satchel")

    def _create_sidecar_file(self, base_path, data):
        sidecar_path = base_path.replace(self._extension, ".json")

        with open(sidecar_path, 'w') as handle:
            json.dump(data, handle, indent=4)

        return sidecar_path

    def create_source(self, context, name, description=None):
        clean_name = self.pack_name(name)

        # The file name consists of the user name and the description, separated
        # by a :.
        file_name = "{}:{}{}".format(context, clean_name, self._extension)

        file_path = os.path.join(self._base_path, file_name)

        sidecar_data = {
            "author": getpass.getuser(),
            "name": name,
            "context": context,
            "date": ht.ui.paste.utils.date_to_string(datetime.datetime.now())
        }

        if description is not None:
            sidecar_data["description"] = description

        sidecar_path = self._create_sidecar_file(file_path, sidecar_data)

        source = CPIOContextCopyPasteItemFile(file_path, context, name, sidecar_path)

        context_sources = self.sources.setdefault(context, [])
        context_sources.append(source)

        return source

    def destroy_item(self, item):
        context_sources = self.sources.get(item.context, {})

        if item in context_sources:
            item.destroy()
            context_sources.remove(item)

    def pack_name(self, name):
        return name.replace(" ", "--")

    def unpack_name(self, name):
        return name.replace("--", " ")

    def get_sources(self, context):
        return self.sources.get(context, [])

    def copy_helper_widget(self, *args, **kwargs):
        return ht.ui.paste.widgets.HomeToolDirItemsCopyHelperWidget(self, *args, **kwargs)

    def paste_helper_widget(self, *args, **kwargs):
        return ht.ui.paste.widgets.HomeToolDirItemsPasteHelperWidget(self, *args, **kwargs)

    def refresh(self):
        self.sources.clear()

        self._init_sources()


class VarTmpCPIOSource(CPIOHierarchicalUserFileCopyPasteSource):
    """Copy/Paste items from /var/tmp/copypaste."""

    _base_path = "/var/tmp/copypaste"

    @property
    def display_name(self):
        return "/var/tmp/copypaste"

    @property
    def icon(self):
        return hou.qt.createIcon("book")


# class FileChooserCPIOSource(CPIOFileCopyPasteSource):
#
#     _base_path = None
#
#     @property
#     def display_name(self):
#         return "Choose A File"
#
#     @property
#     def icon(self):
#         return hou.qt.createIcon("SOP_file")
#
#     def copy_helper_widget(self, *args, **kwargs):
#         return ht.ui.paste.widgets.FileChooserCopyHelperWidget(self, *args, **kwargs)
#
#     def paste_helper_widget(self, *args, **kwargs):
#         return ht.ui.paste.widgets.FileChooserPasteHelperWidget(self, *args, **kwargs)



class CopyPasteItemSource(object):
    """Class responsible for loading and saving items from a source."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, context):
        self._context = context

    @abc.abstractproperty
    def author(self):
        pass

    @property
    def context(self):
        return self._context

    @abc.abstractproperty
    def date(self):
        pass

    @abc.abstractproperty
    def description(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractmethod
    def load_items(self, parent):
        pass

    @abc.abstractmethod
    def save_items(self, parent, items):
        pass


class CPIOAuthoredCopyPasteItemFile(CopyPasteItemSource):
    """Class to load and save items from .cpio files."""

    def __init__(self, context, file_path):
        super(CPIOAuthoredCopyPasteItemFile, self).__init__(context)

        self._file_path = file_path

        file_name = os.path.splitext(os.path.basename(file_path))[0]

        components = file_name.split(":")
        self._author = components[0]
        self._description = components[1]


    @property
    def author(self):
        return self._author

    @property
    def description(self):
        return self._description

    @property
    def display_name(self):
        return self.file_path

    @property
    def file_path(self):
        return self._file_path

    def load_items(self, parent):
        parent.loadItemsFromFile(self.file_path)

    def save_items(self, parent, items):
        target_folder = os.path.dirname(self.file_path)

        # Ensure the path exists.
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)

        parent.saveItemsToFile(items, self.file_path)


class CPIOContextCopyPasteItemFile(CopyPasteItemSource):
    """Class to load and save items from .cpio files."""

    _extension = ".cpio"

    def __init__(self, file_path, context, name, sidecar_path=None):
        super(CPIOContextCopyPasteItemFile, self).__init__(context)

        self._author = None
        self._date = None
        self._description = None
        self._file_path = file_path
        self._name = name
        self._sidecar_path = sidecar_path

        self._init_metadata()

    def _init_metadata(self):
        if self._sidecar_path is None:
            self._sidecar_path = self.file_path.replace(self._extension, ".json")

        if os.path.exists(self._sidecar_path):
            with open(self._sidecar_path) as handle:
                sidecar_data = json.load(handle)

        else:
            sidecar_data = None

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

            self._author = getpwuid(stat_data.st_uid).pw_name
            self._date = datetime.datetime.fromtimestamp(stat_data.st_mtime)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.file_path)

    @classmethod
    def from_path(cls, path):
        file_name = os.path.splitext(os.path.basename(path))[0]

        context, name = file_name.split(":")

        name = cls.unpack_name(name)

        return cls(path, context, name)

    @property
    def author(self):
        return self._author

    @property
    def date(self):
        return self._date

    @property
    def description(self):
        return self._description

    @property
    def file_path(self):
        return self._file_path

    @property
    def name(self):
        return self._name

    def destroy(self):
        if self._sidecar_path is not None:
            if os.path.exists(self._sidecar_path):
                os.remove(self._sidecar_path)

        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def load_items(self, parent):
        parent.loadItemsFromFile(self.file_path)

    def save_items(self, parent, items):
        target_folder = os.path.dirname(self.file_path)

        # Ensure the path exists.
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)

        parent.saveItemsToFile(items, self.file_path)

    @staticmethod
    def pack_name(name):
        return name.replace(" ", "--")

    @staticmethod
    def unpack_name(name):
        return name.replace("--", " ")

