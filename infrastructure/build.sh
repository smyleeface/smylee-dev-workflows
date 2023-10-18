#!/bin/bash

# TODO loop through all the functions and build
cd ../smylee_dev_workflows/functions/pull-request-open

# Ensure the build directory exists
mkdir -p build

# Install the Python dependencies from requirements.txt into the build directory
pip install -r requirements.txt -t build

# Copy application code to directory
cp -r handler.py build

# Change to the build directory
cd build

# Create a ZIP file with the installed dependencies
find . -type d -name "__pycache__" -prune -o -type f -print | zip -r ../../../../../application.zip -@

# Change back to the project's root
cd ../../../../infrastructure

# # Clean up the build directory if needed
# rm -r ../smylee_dev_workflows/functions/pull-request-open/build