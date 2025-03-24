#!/bin/bash

# Define repositories to process
repos=(
    "spacy"                     # Spacy (https://github.com/explosion/spacy)
    "transformers"              # Transformers (https://github.com/huggingface/transformers)
    "keras"                     # Keras (https://github.com/keras-team/keras)
    "matplotlib"                # Matplotlib (https://github.com/matplotlib/matplotlib)
    "numpy"                     # Numpy (https://github.com/numpy/numpy)
    "pandas"                    # Pandas (https://github.com/pandas-dev/pandas)
    "pillow"                    # Pillow (https://github.com/python-pillow/pillow)
    "scikit-learn"              # Scikit-learn (https://github.com/scikit-learn/scikit-learn)
    "sqlmap"                    # Sqlmap (https://github.com/sqlmapproject/sqlmap)
    "models"                    # Tensorflow Models (https://github.com/tensorflow/models)
)

# Loop through each repository
for repo in "${repos[@]}"; do
    echo "Processing repository: $repo"
    # Navigate to repository
    cd "$repo" || { echo "Failed to enter $repo"; continue; }
    rm -rf bandit_reports
    mkdir -p bandit_reports

    # Get last 500 non-merge commits
    git log --first-parent --no-merges -n 500 --pretty=format:"%H" | awk '1; END {print ""}' > commits.txt

    # Process commits with sequential numbering
    counter=1
    while read commit; do
        # Skip empty lines and invalid hashes
        [ -z "$commit" ] && continue
        [ ${#commit} -ne 40 ] && continue
        # Force clean checkout
        git checkout -f "$commit"
        # Format counter with leading zeros
        printf -v seq_num "%03d" $counter
        # Generate filename and run Bandit
        bandit -r . -f json -o "bandit_reports/bandit_${seq_num}_${commit:0:7}.json"
        ((counter++))
    done < commits.txt

    # Clean up and return to parent directory
    cd ..
    echo "Completed processing: $repo"
    echo "----------------------------------"
done
