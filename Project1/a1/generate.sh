#!/bin/bash

# Parse command line arguments
INPUT_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_FILE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./generate.sh --input <input_file> --output <output_file>"
            exit 1
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Error: Both --input and --output arguments are required"
    echo "Usage: ./generate.sh --input <input_file> --output <output_file>"
    exit 1
fi

# Run the Python script
python src/generate_output.py --input "$INPUT_FILE" --output "$OUTPUT_FILE"
