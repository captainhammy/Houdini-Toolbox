
from ht.ui.paste.sources import FileChooserCPIOSource, HomeToolDir, SourceManager, VarTmpCPIOSource

MANAGER = SourceManager()

MANAGER.sources.append(VarTmpCPIOSource())
MANAGER.sources.append(HomeToolDir())
MANAGER.sources.append(FileChooserCPIOSource())

