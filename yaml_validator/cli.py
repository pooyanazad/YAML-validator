"""Compatibility alias for :mod:`yamlguard.cli`."""

import sys

from yamlguard import cli as _implementation

sys.modules[__name__] = _implementation
