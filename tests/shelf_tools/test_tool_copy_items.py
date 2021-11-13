"""Test the tool_copy_items.shelf file."""

# =============================================================================
# TESTS
# =============================================================================


def test_copy_items(mocker, exec_tool_script):
    """Test the copy_items tool."""
    mock_copy = mocker.patch("houdini_toolbox.ui.paste.copy_items")

    mock_kwargs = mocker.MagicMock(spec=dict)
    exec_tool_script("tool_copy_items.shelf", "copy_items", mock_kwargs)

    mock_copy.assert_called_with(mock_kwargs)
