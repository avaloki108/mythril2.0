import pytest

from mythril2.plugin import MythrilPlugin, MythrilPluginLoader
from mythril2.plugin.loader import UnsupportedPluginType


def test_typecheck_load():
    # Arrange
    loader = MythrilPluginLoader()

    # Act
    with pytest.raises(ValueError):
        loader.load(None)


def test_unsupported_plugin_type():
    # Arrange
    loader = MythrilPluginLoader()

    # Act
    with pytest.raises(UnsupportedPluginType):
        loader.load(MythrilPlugin())
