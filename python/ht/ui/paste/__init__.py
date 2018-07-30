
from ht.ui.paste.sources import FileChooserCPIOSource, HomeToolDirSource, SourceManager, VarTmpCPIOSource

MANAGER = SourceManager()

MANAGER.sources.append(VarTmpCPIOSource())
MANAGER.sources.append(HomeToolDirSource())
MANAGER.sources.append(FileChooserCPIOSource())
