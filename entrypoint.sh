#!/bin/bash

# Preserve the existing shell override for debugging the container
if [[ "$1" == "/bin/bash" ]] || [[ "$1" == "bash" ]] || [[ "$1" == "sh" ]] || [[ "$1" == "/bin/sh" ]]; then
    exec "$@"
fi

# Run the validator via the package entry point.
# Also works as: python3 -m yamlguard <args>
exec python3 -m yamlguard "$@"
