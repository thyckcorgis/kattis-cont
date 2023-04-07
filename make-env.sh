#!/bin/sh
# Create virtual environment
# Make sure to exec in the same shell
# and not as subshell by adding a . at the start

# . ./make-env.sh

python3 -m virtualenv .env --python 3.10 &&
    source ./.env/bin/activate &&
    pip install --upgrade pip &&
    pip install -r requirements.txt
