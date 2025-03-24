#!/bin/bash

# Set the module directory and output directory
MODULE_DIR="algorithms/algorithms"
OUTPUT_DIR="algorithms/tests"

# Iterate over each Python file in all subdirectories of the module directory
find "$MODULE_DIR" -type f -name "*.py" | while read -r file; do
    # Skip __init__.py files
    if [[ $(basename "$file") == "__init__.py" ]]; then
        continue
    fi

    # Extract the module name and path
    module_path=$(dirname "$file")
    module_name=$(basename "$file" .py)
    folder_name=$(basename "$module_path")

    # Ensure the output subdirectory exists
    mkdir -p "$OUTPUT_DIR/$folder_name"

    # Run Pynguin
    echo "Running Pynguin for module $module_name in folder $folder_name with module path $module_path"
    pynguin --project-path="$module_path" --module-name="$module_name" --output-path="$OUTPUT_DIR/$folder_name" --export-strategy=PY_TEST
done
