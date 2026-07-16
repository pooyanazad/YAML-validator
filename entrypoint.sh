#!/bin/bash

# If the first argument starts with a dash or is a shell command, execute it directly
if [[ "$1" == "/bin/bash" ]] || [[ "$1" == "bash" ]] || [[ "$1" == "sh" ]] || [[ "$1" == "/bin/sh" ]]; then
    exec "$@"
fi

# Run the validator via the package entry point.
# Also works as: python3 -m yaml_validator <args>
exec python3 /app/app.py "$@"
