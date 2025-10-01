#!/bin/bash

echo "Installing necessary environments for evaluation..."

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model en_core_web_sm..."
python -m spacy download en_core_web_sm

echo "Installation complete!"


