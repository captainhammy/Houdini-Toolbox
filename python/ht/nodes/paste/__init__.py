

from ht.nodes.paste.sources import HomeToolDir, SourceManager, VarTmpCPIOSource

MANAGER = SourceManager()

MANAGER.sources.append(VarTmpCPIOSource())
MANAGER.sources.append(HomeToolDir())


