"""Test the python3.7libs/nodegraphhooks.py module."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
import importlib.util

spec = importlib.util.spec_from_file_location("nodegraphhooks", "houdini/python3.7libs/nodegraphhooks.py")
nodegraphhooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nodegraphhooks)

# Houdini Imports
from canvaseventtypes import KeyboardEvent  # pylint: disable=wrong-import-position


# ==============================================================================
# TESTS
# ==============================================================================


def test_KEY_HIT_TYPES():
    """Test for expected key hit types in nodegraphhooks.KEY_HIT_TYPES."""
    assert nodegraphhooks.KEY_HIT_TYPES == ("keyhit", "menukeyhit", "parentkeyhit")


class Test_createEventHandler:
    """Test nodegraphhooks.createEventHandler."""

    def test_houdini_paste(self, mocker):
        """Test when doing a standard Houdini paste event."""
        mock_is = mocker.patch("ht.ui.nodegraph.is_houdini_paste_event", return_value=True)
        mock_handle = mocker.patch("ht.ui.nodegraph.handle_houdini_paste_event")

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.eventtype = "keyhit"

        mock_pending = mocker.MagicMock(spec=list)

        result = nodegraphhooks.createEventHandler(mock_event, mock_pending)

        assert result == mock_handle.return_value

        mock_is.assert_called_with(mock_event)
        mock_handle.assert_called_with(mock_event)

    def test_copy_items(self, mocker):
        """Test when doing a h.tool:copy_items event."""
        mock_is = mocker.patch("ht.ui.nodegraph.is_houdini_paste_event", return_value=False)
        mock_set = mocker.patch("nodegraphdisplay.setKeyPrompt", return_value=True)
        mock_copy = mocker.patch("ht.ui.paste.copy_items_from_graph")

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.eventtype = "keyhit"

        mock_pending = mocker.MagicMock(spec=list)

        result = nodegraphhooks.createEventHandler(mock_event, mock_pending)

        assert result == mock_copy.return_value

        mock_is.assert_called_with(mock_event)
        mock_set.assert_called_with(mock_event.editor, mock_event.key, "h.tool:copy_items", mock_event.eventtype)
        mock_copy.assert_called_with(mock_event.editor)

    def test_paste_items(self, mocker):
        """Test when doing a h.tool:paste_items event."""
        mock_is = mocker.patch("ht.ui.nodegraph.is_houdini_paste_event", return_value=False)
        mock_set = mocker.patch("nodegraphdisplay.setKeyPrompt", side_effect=(False, True))
        mock_copy = mocker.patch("ht.ui.paste.copy_items_from_graph")
        mock_paste = mocker.patch("ht.ui.paste.paste_items_to_graph")

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.eventtype = "keyhit"

        mock_pending = mocker.MagicMock(spec=list)

        result = nodegraphhooks.createEventHandler(mock_event, mock_pending)

        assert result == mock_paste.return_value

        mock_is.assert_called_with(mock_event)
        mock_set.assert_has_calls(
            [
                mocker.call(mock_event.editor, mock_event.key, "h.tool:copy_items", mock_event.eventtype),
                mocker.call(mock_event.editor, mock_event.key, "h.tool:paste_items", mock_event.eventtype),
            ]
        )
        mock_copy.assert_not_called()
        mock_paste.assert_called_with(mock_event.eventtype, mock_event.editor, mock_event)

    def test_other_key_hit(self, mocker):
        """Test when the event is something we don't care about."""
        mock_is = mocker.patch("ht.ui.nodegraph.is_houdini_paste_event", return_value=False)
        mock_set = mocker.patch("nodegraphdisplay.setKeyPrompt", return_value=False)

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.eventtype = "keyhit"

        mock_pending = mocker.MagicMock(spec=list)

        result = nodegraphhooks.createEventHandler(mock_event, mock_pending)

        assert result == (None, False)

        mock_is.assert_called_with(mock_event)
        mock_set.assert_has_calls(
            [
                mocker.call(mock_event.editor, mock_event.key, "h.tool:copy_items", mock_event.eventtype),
                mocker.call(mock_event.editor, mock_event.key, "h.tool:paste_items", mock_event.eventtype),
            ]
        )

    def test_non_keyhit(self, mocker):
        """Test when the eventtype is not a valid type."""
        mock_is = mocker.patch("ht.ui.nodegraph.is_houdini_paste_event", return_value=False)

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_pending = mocker.MagicMock(spec=list)

        result = nodegraphhooks.createEventHandler(mock_event, mock_pending)
        assert result == (None, False)

        mock_is.assert_not_called()

    def test_non_keyboard(self, mocker):
        """Test when the event is not a KeyboardEvent."""
        mock_is = mocker.patch("ht.ui.nodegraph.is_houdini_paste_event", return_value=False)

        mock_event = mocker.MagicMock()
        mock_pending = mocker.MagicMock(spec=list)

        result = nodegraphhooks.createEventHandler(mock_event, mock_pending)
        assert result == (None, False)

        mock_is.assert_not_called()
