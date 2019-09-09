"""Test the ht.sohohooks.aovs.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
from mock import MagicMock, PropertyMock, patch

# Houdini Toolbox Imports
from ht.sohohooks import manager

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(manager)


# =============================================================================
# CLASSES
# =============================================================================

class Test_SohoHookManager(object):
    """Test ht.sohohooks.manager.SohoHookManager object."""

    def test___init__(self):
        """Test the __init__ method."""
        mgr = manager.SohoHookManager()

        assert mgr._hooks == {}

    # Properties

    @patch.object(manager.SohoHookManager, "__init__", lambda x: None)
    def test_hooks(self):
        """Test the 'hooks' property."""
        mock_hooks = MagicMock(spec=dict)

        mgr = manager.SohoHookManager()
        mgr._hooks = mock_hooks

        assert mgr.hooks == mock_hooks

    # Methods

    # call_hook

    @patch.object(manager.SohoHookManager, "hooks", new_callable=PropertyMock)
    @patch.object(manager.SohoHookManager, "__init__", lambda x: None)
    def test_call_hook__func_result_true(self, mock_hooks, patch_soho):
        """Test when a function returns a value that is equivalent to bool(value) == True."""
        mock_hook_name = MagicMock(spec=str)
        mock_hook = MagicMock()
        mock_hook.return_value = True

        mock_hooks.return_value = {mock_hook_name: [mock_hook]}

        mock_arg = MagicMock()
        mock_kwarg = MagicMock()

        mgr = manager.SohoHookManager()

        result = mgr.call_hook(mock_hook_name, mock_arg, foo=mock_kwarg)

        assert result

        mock_hook.assert_called_with(mock_arg, foo=mock_kwarg)

    @patch.object(manager.SohoHookManager, "hooks", new_callable=PropertyMock)
    @patch.object(manager.SohoHookManager, "__init__", lambda x: None)
    def test_call_hook__func_no_result(self, mock_hooks, patch_soho):
        """Test when a function returns no value."""
        mock_hook_name = MagicMock(spec=str)
        mock_hook = MagicMock()
        mock_hook.return_value = None

        mock_hooks.return_value = {mock_hook_name: [mock_hook]}

        mock_arg = MagicMock()
        mock_kwarg = MagicMock()

        mgr = manager.SohoHookManager()

        result = mgr.call_hook(mock_hook_name, mock_arg, foo=mock_kwarg)

        assert not result

        mock_hook.assert_called_with(mock_arg, foo=mock_kwarg)

    @patch.object(manager.SohoHookManager, "hooks", new_callable=PropertyMock)
    @patch.object(manager.SohoHookManager, "__init__", lambda x: None)
    def test_call_hook__error(self, mock_hooks, patch_soho):
        """Test when calling a hook generates an exception."""
        mock_hook_name = MagicMock(spec=str)
        mock_hook = MagicMock()
        mock_hook.side_effect = Exception

        mock_hooks.return_value = {mock_hook_name: [mock_hook]}

        mock_arg = MagicMock()
        mock_kwarg = MagicMock()

        mgr = manager.SohoHookManager()

        result = mgr.call_hook(mock_hook_name, mock_arg, foo=mock_kwarg)

        assert not result

        mock_hook.assert_called_with(mock_arg, foo=mock_kwarg)

        assert patch_soho["IFDapi"].ray_comment.call_count == 2

    # register_hook

    @patch.object(manager.SohoHookManager, "hooks", new_callable=PropertyMock)
    @patch.object(manager.SohoHookManager, "__init__", lambda x: None)
    def test_register_hook(self, mock_hooks):
        """Test registering hooks."""
        hooks = {}
        mock_hooks.return_value = hooks

        mock_hook_name1 = MagicMock(spec=str)
        mock_hook_name3 = MagicMock(spec=str)

        mock_hook1 = MagicMock()
        mock_hook2 = MagicMock()
        mock_hook3 = MagicMock()

        mgr = manager.SohoHookManager()

        mgr.register_hook(mock_hook_name1, mock_hook1)
        mgr.register_hook(mock_hook_name1, mock_hook2)
        mgr.register_hook(mock_hook_name3, mock_hook3)

        expected = {
            mock_hook_name1: [mock_hook1, mock_hook2],
            mock_hook_name3: [mock_hook3]
        }

        assert hooks == expected
