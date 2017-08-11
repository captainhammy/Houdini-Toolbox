from ht.events import SceneEvents, runEvent

# Perform any registered after scene save events.
runEvent(SceneEvents.PostSave, kwargs)

