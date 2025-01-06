"""
Elicit client module for Python
"""

import sys

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping

from . import elicit
from . import api


