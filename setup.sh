#!/bin/bash

PROJECT_ROOT=$(pwd)

echo "Checking if Python is installed..."
if ! command -v python &>/dev/null; then
    echo "Error: Python is not installed. Please install Python and try again."
    exit 1
else
    echo "Python is installed."
fi

echo "Checking if Poetry is installed..."
if ! command -v poetry &>/dev/null; then
    echo "Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python -
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v poetry &>/dev/null; then
        echo "Error: Poetry installation failed. Please install it manually and try again."
        exit 1
    else
        echo "Poetry installed successfully."
    fi
else
    echo "Poetry is already installed."
fi

echo "Setting up virtual environment and installing dependencies using Poetry..."
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    poetry install
    echo "Dependencies installed successfully."
else
    echo "Error: pyproject.toml not found. Please ensure this file exists in the project root."
    exit 1
fi

echo "Activating Poetry virtual environment..."
poetry --version

echo "Virtual environment setup is complete and activated."
echo "To deactivate, exit the shell using the 'exit' command."
