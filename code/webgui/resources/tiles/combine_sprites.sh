#!/bin/bash

# Default direction is vertical
direction="vertical"

# Check for direction flag
if [ "$1" == "-h" ] || [ "$1" == "--horizontal" ]; then
    direction="horizontal"
    shift  # Remove the flag from arguments
elif [ "$1" == "-v" ] || [ "$1" == "--vertical" ]; then
    direction="vertical"
    shift  # Remove the flag from arguments
fi

# Check if at least 2 arguments are provided (at least 1 input + 1 output)
if [ $# -lt 2 ]; then
    echo "Usage: $0 [-h|--horizontal] [-v|--vertical] <input1.png> [input2.png] ... <output.png>"
    echo "Examples:"
    echo "  $0 128.png 129.png 130.png vaporator.png                    # vertical (default)"
    echo "  $0 -v 128.png 129.png 130.png vaporator.png                 # vertical (explicit)"
    echo "  $0 -h 128.png 129.png 130.png vaporator.png                 # horizontal"
    echo "  $0 --horizontal 128.png 129.png 130.png vaporator.png       # horizontal"
    exit 1
fi

# Build arrays by iterating through all arguments
input_files=()
output_file=""

# Add all arguments except the last to input_files
count=1
for arg in "$@"; do
    if [ $count -eq $# ]; then
        # This is the last argument (output file)
        output_file="$arg"
    else
        # This is an input file
        input_files+=("$arg")
    fi
    count=$((count + 1))
done

# Check if input files exist
for file in "${input_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Input file '$file' does not exist."
        exit 1
    fi
done

# Set the append option based on direction
if [ "$direction" == "horizontal" ]; then
    append_option="+append"
    direction_desc="horizontally (left-to-right)"
else
    append_option="-append"
    direction_desc="vertically (top-to-bottom)"
fi

# Use ImageMagick to stack images
# -append stacks images vertically (top-to-bottom)
# +append stacks images horizontally (left-to-right)
# -background transparent preserves transparency
magick -background transparent "${input_files[@]}" $append_option "$output_file"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Successfully combined ${#input_files[@]} images $direction_desc into '$output_file'"
else
    echo "Error: Failed to combine images"
    exit 1
fi