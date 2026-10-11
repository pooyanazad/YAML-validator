"""Compatibility alias for :mod:`yamlguard.output`."""

import sys

from yamlguard import output as _implementation

sys.modules[__name__] = _implementation
