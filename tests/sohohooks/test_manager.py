"""Test the ht.sohohooks.aovs.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.sohohooks import manager

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(manager)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize a manager."""
    mocker.patch.object(manager.SohoHookManager, "__init__", lambda x: None)

    def _create():
        return manager.SohoHookManager()

    return _create


# =============================================================================
# CLASSES
# =============================================================================


class Test_SohoHookManager(object):
    """Test ht.sohohooks.manager.SohoHookManager object."""

    def test___init__(self):
        """Test object initialization."""
        mgr = manager.SohoHookManager()

        assert mgr._hooks == {}

    # Properties

    def test_hooks(self, init_manager, mocker):
        """Test the 'hooks' property."""
        mock_value = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._hooks = mock_value
        assert mgr.hooks == mock_value

    # Methods

    # call_hook

    def test_call_hook__func_result_true(self, init_manager, mocker, patch_soho):
        """Test when a function returns a value that is equivalent to bool(value) == True."""
        mock_hooks = mocker.patch.object(
            manager.SohoHookManager, "hooks", new_callable=mocker.PropertyMock
        )

        mock_hook_name = mocker.MagicMock(spec=str)
        mock_hook = mocker.MagicMock()
        mock_hook.return_value = True

        mock_hooks.return_value = {mock_hook_name: [mock_hook]}

        mock_arg = mocker.MagicMock()
        mock_kwarg = mocker.MagicMock()

        mgr = init_manager()

        result = mgr.call_hook(mock_hook_name, mock_arg, foo=mock_kwarg)

        assert result

        mock_hook.assert_called_with(mock_arg, foo=mock_kwarg)

    def test_call_hook__func_no_result(self, init_manager, mocker, patch_soho):
        """Test when a function returns no value."""
        mock_hooks = mocker.patch.object(
            manager.SohoHookManager, "hooks", new_callable=mocker.PropertyMock
        )

        mock_hook_name = mocker.MagicMock(spec=str)
        mock_hook = mocker.MagicMock()
        mock_hook.return_value = None

        mock_hooks.return_value = {mock_hook_name: [mock_hook]}

        mock_arg = mocker.MagicMock()
        mock_kwarg = mocker.MagicMock()

        mgr = init_manager()

        result = mgr.call_hook(mock_hook_name, mock_arg, foo=mock_kwarg)

        assert not result

        mock_hook.assert_called_with(mock_arg, foo=mock_kwarg)

    def test_call_hook__error(self, init_manager, mocker, patch_soho):
        """Test when calling a hook generates an exception."""
        mock_hooks = mocker.patch.object(
            manager.SohoHookManager, "hooks", new_callable=mocker.PropertyMock
        )

        mock_hook_name = mocker.MagicMock(spec=str)
        mock_hook = mocker.MagicMock()
        mock_hook.side_effect = Exception

        mock_hooks.return_value = {mock_hook_name: [mock_hook]}

        mock_arg = mocker.MagicMock()
        mock_kwarg = mocker.MagicMock()

        mgr = init_manager()

        result = mgr.call_hook(mock_hook_name, mock_arg, foo=mock_kwarg)

        assert not result

        mock_hook.assert_called_with(mock_arg, foo=mock_kwarg)

        assert patch_soho.IFDapi.ray_comment.call_count == 2

    # register_hook

    def test_register_hook(self, init_manager, mocker):
        """Test registering hooks."""
        mock_hooks = mocker.patch.object(
            manager.SohoHookManager, "hooks", new_callable=mocker.PropertyMock
        )

        hooks = {}
        mock_hooks.return_value = hooks

        mock_hook_name1 = mocker.MagicMock(spec=str)
        mock_hook_name3 = mocker.MagicMock(spec=str)

        mock_hook1 = mocker.MagicMock()
        mock_hook2 = mocker.MagicMock()
        mock_hook3 = mocker.MagicMock()

        mgr = init_manager()

        mgr.register_hook(mock_hook_name1, mock_hook1)
        mgr.register_hook(mock_hook_name1, mock_hook2)
        mgr.register_hook(mock_hook_name3, mock_hook3)

        expected = {
            mock_hook_name1: [mock_hook1, mock_hook2],
            mock_hook_name3: [mock_hook3],
        }

        assert hooks == expected
