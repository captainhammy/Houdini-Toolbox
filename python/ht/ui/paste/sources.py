

import abc
import getpass
import os
import re

import hou


class SourceManager(object):

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


class CPIOFileCopyPasteSource(CopyPasteSource):
    """Class responsible for handling cpio file sources arranged in context folders."""

    def __init__(self):
        super(CPIOFileCopyPasteSource, self).__init__()

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

            for p in sorted(files):
                if re.match("\w+:[\w_-]+\.cpio", p) is not None:
                    context_sources.append(CPIOCopyPasteItemSource(context, os.path.join(context_path, p)))

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

        source = CPIOCopyPasteItemSource(context, file_path)

        context_sources = self.sources.setdefault(context, [])
        context_sources.append(source)

        return source

    def get_sources(self, context):
        return self.sources.get(context, [])


class HomeToolDir(CPIOFileCopyPasteSource):
    """Copy/Paste items from ~/tooldev/copypaste."""
    _base_path = os.path.join(os.path.expanduser("~"), "tooldev", "copypaste")

    @property
    def display_name(self):
        return "~/tooldev"

    @property
    def icon(self):
        return hou.qt.createIcon("MISC_satchel")


class VarTmpCPIOSource(CPIOFileCopyPasteSource):
    """Copy/Paste items from /var/tmp/copypaste."""

    _base_path = "/var/tmp/copypaste"

    @property
    def display_name(self):
        return "/var/tmp/copypaste"

    @property
    def icon(self):
        return hou.qt.createIcon("book")


class FileChooserCPIOSource(CPIOFileCopyPasteSource):

     _base_path = None

     @property
     def display_name(self):
         return "Choose A File"

     @property
     def icon(self):
         return hou.qt.createIcon("SOP_file")



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
    def description(self):
        pass

    @abc.abstractproperty
    def display_name(self):
        pass

    @abc.abstractmethod
    def load_items(self, parent):
        pass

    @abc.abstractmethod
    def save_items(self, parent, items):
        pass


class CPIOCopyPasteItemSource(CopyPasteItemSource):
    """Class to load and save items from .cpio files."""

    def __init__(self, context, file_path):
        super(CPIOCopyPasteItemSource, self).__init__(context)

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