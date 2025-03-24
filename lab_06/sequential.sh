#!/bin/bash

# Define the directory for log files and the results file
LOG_DIR="algorithms/seqential"
RESULTS_FILE="algorithms/sequential.csv"
mkdir -p "$LOG_DIR"

# Write the CSV header to the results file
echo "rep,elapsed,fail_count,failed_tests" > "$RESULTS_FILE"

# Run tests sequentially for 10 repetitions
for rep in {1..10}; do
    echo "Sequential run, repetition $rep"
    log_file="$LOG_DIR/seq_rep${rep}.log"
    start=$(date +%s.%N)
    pytest > "$log_file" 2>&1
    end=$(date +%s.%N)
    elapsed=$(echo "$end - $start" | bc)

    # Count number of failures
    fail_count=$(grep -c "FAILED" "$log_file" || true)

    # Extract names of failed tests
    failed_tests=$(grep "FAILED" "$log_file" | tr '\n' ';' | sed 's/;$//')

    # Write the result as a CSV row
    echo "$rep,$elapsed,$fail_count,\"$failed_tests\"" >> "$RESULTS_FILE"
done