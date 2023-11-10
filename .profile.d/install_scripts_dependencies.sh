#!/usr/bin/env bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Use python -m pip to install script dependencies
python -m pip install -r requirements_scripts.txt

# Deactivate the virtual environment
deactivate
