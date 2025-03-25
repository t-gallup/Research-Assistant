#!/bin/bash
set -e

# Check if the handler is set
if [ -z "$_HANDLER" ]; then
  _HANDLER="$1"
fi

# Run the handler with awslambdaric
exec python -m awslambdaric "$_HANDLER"