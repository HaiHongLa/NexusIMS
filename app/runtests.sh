#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 [unittest|coverage]"
    exit 1
}

# Check if the correct number of arguments are provided
if [ $# -ne 1 ]; then
    usage
fi

# Check the provided argument and run the corresponding command
if [ "$1" == "unittest" ]; then
    echo "Running unittest..."
    PYTHONWARNINGS=ignore python3 -m unittest discover -s tests -p 'test*.py'
elif [ "$1" == "coverage" ]; then
    echo "Running coverage..."
    PYTHONWARNINGS=ignore coverage run --omit=/usr/* -m unittest discover -s tests -p 'test*.py'
    coverage report
elif [ "$1" == "clean" ]; then
    rm .coverage coverage.xml
else
    usage
fi