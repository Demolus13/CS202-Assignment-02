#!/bin/bash

# Define the directory for log files and the results file
LOG_DIR="algorithms/parallel"
RESULTS_FILE="algorithms/parallel.csv"
mkdir -p "$LOG_DIR"

# Write the CSV header to the results file
echo "dist_mode,workers,threads,rep,elapsed,fail_count,failed_tests" > "$RESULTS_FILE"

# Define configurations:
# We use two options for worker/thread counts: "auto" and "1".
# And two pytest-xdist distribution modes: "load" and "no".
for dist_mode in load no; do
    for config in "auto,auto" "auto,1" "1,auto" "1,1"; do
        IFS=',' read workers threads <<< "$config"
        for rep in {1..3}; do
            echo "Parallel run: --dist $dist_mode, -n $workers, --parallel-threads $threads, repetition $rep"
            log_file="$LOG_DIR/par_${dist_mode}_${workers}_${threads}_rep${rep}.log"
            start=$(date +%s.%N)
            pytest -n "$workers" --dist "$dist_mode" --parallel-threads "$threads" > "$log_file" 2>&1
            end=$(date +%s.%N)
            elapsed=$(echo "$end - $start" | bc)

            # Count number of failures
            fail_count=$(grep -c "FAILED" "$log_file" || true)

            # Extract names of failed tests
            failed_tests=$(grep "FAILED" "$log_file" | tr '\n' ';' | sed 's/;$//')
            
            # Write the result as a CSV row
            echo "$dist_mode,$workers,$threads,$rep,$elapsed,$fail_count,\"$failed_tests\"" >> "$RESULTS_FILE"
        done
    done
done
