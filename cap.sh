#!/bin/bash

source "$(dirname "$0")/config.sh"

python3 "${CAPITALIZE_SCRIPT}" "$@"
