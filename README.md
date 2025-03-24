# CS202: Software Tools and Techniques for CSE – Lab Reports and Scripts

---

## Overview

The lab assignments cover the following topics:
- **Lab 05:** Automated unit test execution and coverage analysis using pytest, coverage.py, and Pynguin.
- **Lab 06:** Evaluation of sequential and parallel test execution performance (using pytest-xdist and pytest-run-parallel).
- **Lab 07 & 08:** Security vulnerability analysis of open-source repositories using Bandit, with an emphasis on identifying common weaknesses (e.g., CWE-703).

---

## Environment Setup

### Required Tools and Versions
- **pytest:** v8.3.4  
- **pytest-cov:** v6.0.0  
- **pytest-func-cov:** v0.2.3  
- **coverage:** v7.6.12  
- **pynguin:** v0.40.0  
- **pytest-xdist:** v3.6.1  
- **pytest-run-parallel:** v0.3.1  
- **bandit:** v1.8.3

### Repository Setup
Clone the target repository (e.g., [keon/algorithms](https://github.com/keon/algorithms)) and checkout the specified commit hash (`cad4754bc71742c2d6fcbd3b92ae74834d359844`) before running the tests.

---

## Lab Activities and Instructions

### Lab 05 – Unit Test Execution, Coverage Analysis & Test Generation

1. **Running Existing Tests (Test Suite A):**
   ```bash
   python3 -m pytest tests
   ```

2. **Code Coverage Analysis:**
   ```bash
   coverage run --branch --source=algorithms -m pytest
   coverage report -m
   coverage html
   ```

3. **Automated Unit Test Generation with Pynguin:**
   The provided bash script iterates over Python files (skipping `__init__.py` files) to generate test cases:
   ```bash
   find $MODULE_DIR -type f -name "*.py" | while read -r file; do
       if [[ $(basename "$file") == "__init__.py" ]]; then
           continue
       fi
       module_path=$(dirname "$file")
       module_name=$(basename "$file" .py)
       folder_name=$(basename "$module_path")
       mkdir -p "$OUTPUT_DIR/$folder_name"
       echo "Running Pynguin for module $module_name in folder $folder_name with module path $module_path"
       pynguin --project-path="$module_path" --module-name="$module_name" --output-path="$OUTPUT_DIR/$folder_name" --export-strategy=PY_TEST
   done
   ```
   After generating tests, run them with:
   ```bash
   python3 -m pytest tests
   ```

---

### Lab 06 – Parallel Test Execution and Performance Analysis

1. **Sequential Test Execution:**
   A minimal `pytest.ini` configuration specifies the test directory:
   ```ini
   [pytest]
   testpaths =
       tests
   ```

2. **Parallel Test Execution Script:**
   A bash script is used to run tests in parallel with different configurations (workers, threads, and distribution modes). It logs output, measures execution time, and captures any failures:
   ```bash
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
               fail_count=$(grep -c "FAILED" "$log_file" || true)
               failed_tests=$(grep "FAILED" "$log_file" | tr '\n' ';' | sed 's/;$//')
               echo "$dist_mode,$workers,$threads,$rep,$elapsed,$fail_count,\"$failed_tests\"" >> "$RESULTS_FILE"
           done
       done
   done
   ```

---

### Labs 07 & 08 – Vulnerability Analysis with Bandit

1. **Bandit Execution Script:**
   This script processes multiple repositories by checking out the last 500 non-merge commits and running Bandit on each commit:
   ```bash
   # Define repositories to process
   repos=(
       "/path/to/spacy"            # Spacy (https://github.com/explosion/spacy)
       "/path/to/transformers"     # Transformers (https://github.com/huggingface/transformers)
       "/path/to/keras"            # Keras (https://github.com/keras-team/keras)
       "/path/to/matplotlib"       # Matplotlib (https://github.com/matplotlib/matplotlib)
       "/path/to/numpy"            # Numpy (https://github.com/numpy/numpy)
       "/path/to/pandas"           # Pandas (https://github.com/pandas-dev/pandas)
       "/path/to/pillow"           # Pillow (https://github.com/python-pillow/pillow)
       "/path/to/scikit-learn"     # Scikit-learn (https://github.com/scikit-learn/scikit-learn)
       "/path/to/sqlmap"           # Sqlmap (https://github.com/sqlmapproject/sqlmap)
       "/path/to/tensorflow-models" # Tensorflow Models (https://github.com/tensorflow/models)
   )

   # Loop through each repository
   for repo in "${repos[@]}"; do
       echo "Processing repository: $repo"
       cd "$repo" || { echo "Failed to enter $repo"; continue; }
       rm -rf bandit_reports
       mkdir -p bandit_reports
       git log --first-parent --no-merges -n 500 --pretty=format:"%H" | awk '1; END {print ""}' > commits.txt
       counter=1
       while read commit; do
           [ -z "$commit" ] && continue
           [ ${#commit} -ne 40 ] && continue
           git checkout -f "$commit"
           printf -v seq_num "%03d" $counter
           bandit -r . -f json -o "bandit_reports/bandit_${seq_num}_${commit:0:7}.json"
           ((counter++))
       done < commits.txt
       cd ..
       echo "Completed processing: $repo"
       echo "----------------------------------"
   done
   ```

2. **Repository-Level Vulnerability Analysis:**
   After Bandit execution, Python scripts are used to aggregate and analyze vulnerability metrics (e.g., confidence levels and severity statistics). An example snippet:
   ```python
   # Aggregate vulnerability metrics from Bandit reports
   high_conf = sum(file_metrics.get("CONFIDENCE.HIGH", 0) for file_metrics in metrics.values())
   med_conf = sum(file_metrics.get("CONFIDENCE.MEDIUM", 0) for file_metrics in metrics.values())
   low_conf = sum(file_metrics.get("CONFIDENCE.LOW", 0) for file_metrics in metrics.values())
   
   high_values = [file_metrics.get("SEVERITY.HIGH", 0) for file_metrics in metrics.values()]
   med_values = [file_metrics.get("SEVERITY.MEDIUM", 0) for file_metrics in metrics.values()]
   low_values = [file_metrics.get("SEVERITY.LOW", 0) for file_metrics in metrics.values()]
   
   high_sev_sum = sum(high_values)
   med_sev_sum = sum(med_values)
   low_sev_sum = sum(low_values)
   
   high_sev_min = min(high_values) if high_values else 0
   high_sev_max = max(high_values) if high_values else 0
   high_sev_avg = sum(high_values) / len(high_values) if high_values else 0
   
   med_sev_min = min(med_values) if med_values else 0
   med_sev_max = max(med_values) if med_values else 0
   med_sev_avg = sum(med_values) / len(med_values) if med_values else 0
   
   low_sev_min = min(low_values) if low_values else 0
   low_sev_max = max(low_values) if low_values else 0
   low_sev_avg = sum(low_values) / len(low_values) if low_values else 0
   ```
