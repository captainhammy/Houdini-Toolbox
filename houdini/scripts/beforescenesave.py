from ht.events import SceneEvents, runEvent

# Perform any registered before scene save events.
runEvent(SceneEvents.PreSave, kwargs)

