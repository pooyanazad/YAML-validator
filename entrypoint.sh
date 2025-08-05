#!/bin/bash

# If the first argument starts with a dash or is a shell command, execute it directly
if [[ "$1" == "/bin/bash" ]] || [[ "$1" == "bash" ]] || [[ "$1" == "sh" ]] || [[ "$1" == "/bin/sh" ]]; then
    exec "$@"
fi

# Otherwise, run the Python app with the provided arguments
exec python /app/app.py "$@"