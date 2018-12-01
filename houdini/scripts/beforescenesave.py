from ht.events import SceneEvents, run_event

# Perform any registered before scene save events.
run_event(SceneEvents.PreSave, kwargs)

