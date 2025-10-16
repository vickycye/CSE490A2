#!/bin/bash

# No additional packages needed - using Python standard library only
echo "Starting team assignment process..."

# Copy the CSV file to the workspace if it exists
if [ -f "../cse403-preferences.csv" ]; then
    cp ../cse403-preferences.csv ./cse403-preferences.csv
elif [ -f "../Project2/cse403-preferences.csv" ]; then
    cp ../Project2/cse403-preferences.csv ./cse403-preferences.csv
fi

# Run the team assignment script
echo "Running team assignment..."
python3 team_assignment.py cse403-preferences.csv /workspace/out.csv

echo "Team assignment complete! Output saved to /workspace/out.csv"

