# We use RsT document formatting in docstring. For example :param to mark parameters.
# See PEP 287
__docformat__ = "restructuredtext"
import logging

from mythril2.plugin.loader import MythrilPluginLoader

# Accept mythril.VERSION to get mythril's current version number
from .__version__ import __version__ as VERSION

log = logging.getLogger(__name__)
