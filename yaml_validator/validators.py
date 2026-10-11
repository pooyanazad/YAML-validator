"""Compatibility alias for :mod:`yamlguard.validators`."""

import sys

from yamlguard import validators as _implementation

sys.modules[__name__] = _implementation
