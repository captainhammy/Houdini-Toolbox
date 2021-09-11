"""Test the ht.ui.nodegraph module."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Houdini Toolbox
import ht.ui.nodegraph

# Houdini
from canvaseventtypes import KeyboardEvent

# ==============================================================================
# TESTS
# ==============================================================================


class Test_handle_houdini_paste_event:
    """Test ht.ui.nodegraph.handle_houdini_paste_event."""

    def test_menukeyhit(self, mocker):
        """Test when the eventtype is "menukeyhit"."""
        mock_undos = mocker.patch("hou.undos.group")

        mock_editor = mocker.MagicMock()

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.editor = mock_editor
        mock_event.eventtype = "menukeyhit"

        mock_paste = mocker.patch("nodegraphutils.pasteItems")
        mock_move = mocker.patch("nodegraphutils.moveItemsToLocation")
        mock_update = mocker.patch("nodegraphutils.updateCurrentItem")

        mock_run_event = mocker.patch("ht.ui.nodegraph.EVENT_MANAGER.run_event")

        result = ht.ui.nodegraph.handle_houdini_paste_event(mock_event)

        assert result == (None, True)

        mock_undos.assert_called_with("Paste from clipboard")

        mock_paste.assert_called_with(mock_editor)

        mock_editor.posFromScreen.assert_called_with(mock_editor.screenBounds().center())

        mock_move.assert_called_with(mock_editor, mock_editor.posFromScreen(), mock_editor.screenBounds().center())
        mock_update.assert_called_with(mock_editor)

        scriptargs = {"items": mock_editor.pwd().selectedItems(), "uievent": mock_event}
        mock_run_event.assert_called_with(ht.ui.nodegraph.KeyboardEvents.PostPasteEvent, scriptargs)

    def test_keyhit(self, mocker):
        """Test when the eventtype is "keyhit"."""
        mock_undos = mocker.patch("hou.undos.group")

        mock_editor = mocker.MagicMock()

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.editor = mock_editor

        mock_paste = mocker.patch("nodegraphutils.pasteItems")
        mock_move = mocker.patch("nodegraphutils.moveItemsToLocation")
        mock_update = mocker.patch("nodegraphutils.updateCurrentItem")

        mock_run_event = mocker.patch("ht.ui.nodegraph.EVENT_MANAGER.run_event")

        result = ht.ui.nodegraph.handle_houdini_paste_event(mock_event)

        assert result == (None, True)

        mock_undos.assert_called_with("Paste from clipboard")

        mock_paste.assert_called_with(mock_editor)

        mock_editor.posFromScreen.assert_called_with(mock_event.mousepos)

        mock_move.assert_called_with(mock_editor, mock_editor.posFromScreen(), mock_event.mousepos)
        mock_update.assert_called_with(mock_editor)

        scriptargs = {"items": mock_editor.pwd().selectedItems(), "uievent": mock_event}
        mock_run_event.assert_called_with(ht.ui.nodegraph.KeyboardEvents.PostPasteEvent, scriptargs)

    def test_parentkeyhit(self, mocker):
        """Test when the eventtype is "parentkeyhit"."""
        mock_undos = mocker.patch("hou.undos.group")

        mock_editor = mocker.MagicMock()

        mock_event = mocker.MagicMock(spec=KeyboardEvent)
        mock_event.editor = mock_editor
        mock_event.eventtype = "parentkeyhit"

        mock_paste = mocker.patch("nodegraphutils.pasteItems")
        mock_move = mocker.patch("nodegraphutils.moveItemsToLocation")
        mock_update = mocker.patch("nodegraphutils.updateCurrentItem")

        mock_run_event = mocker.patch("ht.ui.nodegraph.EVENT_MANAGER.run_event")

        result = ht.ui.nodegraph.handle_houdini_paste_event(mock_event)

        assert result == (None, True)

        mock_undos.assert_called_with("Paste from clipboard")

        mock_paste.assert_called_with(mock_editor)

        mock_move.assert_not_called()
        mock_update.assert_called_with(mock_editor)

        scriptargs = {"items": mock_editor.pwd().selectedItems(), "uievent": mock_event}
        mock_run_event.assert_called_with(ht.ui.nodegraph.KeyboardEvents.PostPasteEvent, scriptargs)


def test_is_houdini_paste_event(mocker):
    """Test ht.ui.nodegraph.is_houdini_paste_event."""
    mock_event = mocker.MagicMock()
    mock_set = mocker.patch("ht.ui.nodegraph.setKeyPrompt")

    result = ht.ui.nodegraph.is_houdini_paste_event(mock_event)

    assert result == mock_set.return_value

    mock_set.assert_called_with(mock_event.editor, mock_event.key, "h.paste", mock_event.eventtype)
