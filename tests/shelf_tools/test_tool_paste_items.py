"""Test the tool_paste_items.shelf file."""

# =============================================================================
# TESTS
# =============================================================================


def test_paste_items(mocker, exec_tool_script):
    """Test the paste_items tool."""
    mock_paste = mocker.patch("ht.ui.paste.paste_items")

    mock_kwargs = mocker.MagicMock(spec=dict)
    exec_tool_script("tool_paste_items.shelf", "paste_items", mock_kwargs)

    mock_paste.assert_called_with(mock_kwargs)
