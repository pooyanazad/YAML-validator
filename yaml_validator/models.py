"""Compatibility alias for :mod:`yamlguard.models`."""

import sys

from yamlguard import models as _implementation

sys.modules[__name__] = _implementation
