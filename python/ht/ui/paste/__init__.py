
from ht.ui.paste.sources import HomeToolDirSource, SourceManager, VarTmpCPIOSource
#from ht.ui.paste.sources import FileChooserCPIOSource,

MANAGER = SourceManager()

#MANAGER.sources.append(VarTmpCPIOSource())
MANAGER.sources.append(HomeToolDirSource())
#MANAGER.sources.append(FileChooserCPIOSource())
