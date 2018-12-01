from ht.events import SceneEvents, run_event

# Perform any registered after scene save events.
run_event(SceneEvents.PostSave, kwargs)

