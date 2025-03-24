#!/usr/bin/env python3
import os
import glob
import json
import collections
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

def parse_bandit_report(filepath, repository_name):
    basename = os.path.basename(filepath)
    parts = basename.split('_')
    if len(parts) < 3:
        return None
    try:
        seq_num = int(parts[1])
    except ValueError:
        seq_num = None
    commit_hash = parts[2].split('.')[0]

    with open(filepath, 'r') as f:
        try:
            report = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {filepath}")
            return None

    # Extract unique CWEs from "results" if present.
    cwe_list = []
    if "results" in report:
        for issue in report.get("results", []):
            cwe_info = issue.get("issue_cwe", {})
            if cwe_info and "id" in cwe_info:
                cwe_list.append(f"CWE-{cwe_info['id']}")
    else:
        cwe_list = []

    # Process metrics if present.
    metrics = report.get("metrics", {})
    # Aggregate confidence values
    high_conf = sum(file_metrics.get("CONFIDENCE.HIGH", 0) for file_metrics in metrics.values())
    med_conf  = sum(file_metrics.get("CONFIDENCE.MEDIUM", 0) for file_metrics in metrics.values())
    low_conf  = sum(file_metrics.get("CONFIDENCE.LOW", 0) for file_metrics in metrics.values())

    # For severity, compute file-level values and then min, max, avg, and sum.
    high_values = [file_metrics.get("SEVERITY.HIGH", 0) for file_metrics in metrics.values()]
    med_values  = [file_metrics.get("SEVERITY.MEDIUM", 0) for file_metrics in metrics.values()]
    low_values  = [file_metrics.get("SEVERITY.LOW", 0) for file_metrics in metrics.values()]

    high_sev_sum = sum(high_values)
    med_sev_sum  = sum(med_values)
    low_sev_sum  = sum(low_values)

    high_sev_min = min(high_values) if high_values else 0
    high_sev_max = max(high_values) if high_values else 0
    high_sev_avg = sum(high_values)/len(high_values) if high_values else 0

    med_sev_min = min(med_values) if med_values else 0
    med_sev_max = max(med_values) if med_values else 0
    med_sev_avg = sum(med_values)/len(med_values) if med_values else 0

    low_sev_min = min(low_values) if low_values else 0
    low_sev_max = max(low_values) if low_values else 0
    low_sev_avg = sum(low_values)/len(low_values) if low_values else 0

    data = {
        "repository": repository_name,
        "high_conf": high_conf,
        "med_conf": med_conf,
        "low_conf": low_conf,
        "high_sev_sum": high_sev_sum,
        "med_sev_sum": med_sev_sum,
        "low_sev_sum": low_sev_sum,
        "high_sev_min": high_sev_min,
        "high_sev_max": high_sev_max,
        "high_sev_avg": high_sev_avg,
        "med_sev_min": med_sev_min,
        "med_sev_max": med_sev_max,
        "med_sev_avg": med_sev_avg,
        "low_sev_min": low_sev_min,
        "low_sev_max": low_sev_max,
        "low_sev_avg": low_sev_avg,
        "cwes": list(cwe_list)
    }

    return (seq_num, commit_hash, data)

def main():
    # Specify which repositories to process
    repositories_to_process = [
        "spacy",                     # Spacy (https://github.com/explosion/spacy)
        "transformers",              # Transformers (https://github.com/huggingface/transformers)
        "keras",                     # Keras (https://github.com/keras-team/keras)
        "matplotlib",                # Matplotlib (https://github.com/matplotlib/matplotlib)
        "numpy",                     # Numpy (https://github.com/numpy/numpy)
        "pandas",                    # Pandas (https://github.com/pandas-dev/pandas)
        "pillow",                    # Pillow (https://github.com/python-pillow/pillow)
        "scikit-learn",              # Scikit-learn (https://github.com/scikit-learn/scikit-learn)
        "sqlmap",                    # Sqlmap (https://github.com/sqlmapproject/sqlmap)
        "models"                     # Tensorflow Models (https://github.com/tensorflow/models)
    ]

    for repo in repositories_to_process:
        print(f"Processing repository: {repo}")
        # Create the bandit_results folder inside the repository if it doesn't exist
        results_folder = os.path.join(repo, "bandit_results")
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
            print(f"Created folder: {results_folder}")

        # Locate the bandit_reports folder within the repository
        bandit_dir = os.path.join(repo, "bandit_reports")
        if not os.path.isdir(bandit_dir):
            print(f"Directory {bandit_dir} not found. Skipping repository {repo}.")
            continue

        pattern = os.path.join(bandit_dir, "bandit_*.json")
        report_files = glob.glob(pattern)
        report_files.sort()
        print(f"Found {len(report_files)} report(s) in {bandit_dir}...")

        commit_data = []
        for filepath in tqdm(report_files, desc=f"Processing reports in {repo}", unit="report"):
            result = parse_bandit_report(filepath, repo)
            if result is not None:
                commit_data.append(result)

        if not commit_data:
            print(f"No commit data found for repository {repo}!")
            continue

        # Convert the tuple array into a DataFrame for easier analysis.
        rows = []
        for tup in commit_data:
            seq_num, commit_hash, data = tup
            tup_cwes = list(set(data.get("cwes", [])))
            tup_cwes.sort()
            row = {
                "repository": data.get("repository"),
                "seq": seq_num,
                "commit": commit_hash,
                "high_conf": data.get("high_conf", 0),
                "med_conf": data.get("med_conf", 0),
                "low_conf": data.get("low_conf", 0),
                "high_sev_sum": data.get("high_sev_sum", 0),
                "med_sev_sum": data.get("med_sev_sum", 0),
                "low_sev_sum": data.get("low_sev_sum", 0),
                "high_sev_min": data.get("high_sev_min", 0),
                "high_sev_max": data.get("high_sev_max", 0),
                "high_sev_avg": data.get("high_sev_avg", 0),
                "med_sev_min": data.get("med_sev_min", 0),
                "med_sev_max": data.get("med_sev_max", 0),
                "med_sev_avg": data.get("med_sev_avg", 0),
                "low_sev_min": data.get("low_sev_min", 0),
                "low_sev_max": data.get("low_sev_max", 0),
                "low_sev_avg": data.get("low_sev_avg", 0),
                "cwes": ", ".join(tup_cwes)
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Save the aggregated commit data CSV into the bandit_results folder
        csv_path = os.path.join(results_folder, "aggregated_commit_data.csv")
        df.to_csv(csv_path, index=False)
        print(f"Aggregated commit data saved to {csv_path}")

        # Plotting separate severity trends for this repository (sum values)
        df.sort_values(by="seq", inplace=True)
        severity_types = [
            ("High Severity", "high_sev_sum"),
            ("Medium Severity", "med_sev_sum"),
            ("Low Severity", "low_sev_sum")
        ]
        for severity_label, severity_col in severity_types:
            plt.figure(figsize=(10, 6))
            plt.plot(df['seq'], df[severity_col], marker='o', label=severity_label)
            plt.xlabel("Commit Sequence")
            plt.ylabel("Total Count")
            plt.title(f"{severity_label} Trends in {repo}")
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plot_filename = os.path.join(results_folder, f"{severity_label.lower().replace(' ', '_')}_trends_{repo}.png")
            plt.savefig(plot_filename)
            plt.close()
            print(f"Saved {severity_label} trend plot for {repo} as {plot_filename}")

        # Plotting additional severity statistics (min, max, average) for each severity
        severity_stats = [
            ("High Severity", "high_sev_min", "high_sev_max", "high_sev_avg"),
            ("Medium Severity", "med_sev_min", "med_sev_max", "med_sev_avg"),
            ("Low Severity", "low_sev_min", "low_sev_max", "low_sev_avg")
        ]
        for severity_label, stat_min, stat_max, stat_avg in severity_stats:
            
            # Plot minimum values
            plt.figure(figsize=(10,6))
            plt.plot(df['seq'], df[stat_min], marker='o', label=f"{severity_label} Min")
            plt.xlabel("Commit Sequence")
            plt.ylabel("Count")
            plt.title(f"{severity_label} Minimum Trends in {repo}")
            plt.legend()
            plt.tight_layout()
            min_plot_path = os.path.join(results_folder, f"{severity_label.lower().replace(' ', '_')}_min_trends_{repo}.png")
            plt.savefig(min_plot_path)
            plt.close()
            print(f"Saved {severity_label} minimum trend plot for {repo} as {min_plot_path}")

            # Plot maximum values
            plt.figure(figsize=(10,6))
            plt.plot(df['seq'], df[stat_max], marker='o', label=f"{severity_label} Max")
            plt.xlabel("Commit Sequence")
            plt.ylabel("Count")
            plt.title(f"{severity_label} Maximum Trends in {repo}")
            plt.legend()
            plt.tight_layout()
            max_plot_path = os.path.join(results_folder, f"{severity_label.lower().replace(' ', '_')}_max_trends_{repo}.png")
            plt.savefig(max_plot_path)
            plt.close()
            print(f"Saved {severity_label} maximum trend plot for {repo} as {max_plot_path}")

            # Plot average values
            plt.figure(figsize=(10,6))
            plt.plot(df['seq'], df[stat_avg], marker='o', label=f"{severity_label} Average")
            plt.xlabel("Commit Sequence")
            plt.ylabel("Count")
            plt.title(f"{severity_label} Average Trends in {repo}")
            plt.legend()
            plt.tight_layout()
            avg_plot_path = os.path.join(results_folder, f"{severity_label.lower().replace(' ', '_')}_avg_trends_{repo}.png")
            plt.savefig(avg_plot_path)
            plt.close()
            print(f"Saved {severity_label} average trend plot for {repo} as {avg_plot_path}")

        # Aggregated CWE Frequency for this repository
        repo_cwes = []
        for tup in commit_data:
            _, _, data = tup
            repo_cwes.extend(data.get("cwes", []))

        if repo_cwes:
            cwe_counter = collections.Counter(repo_cwes)
            cwe_items = sorted(cwe_counter.items(), key=lambda x: x[1], reverse=True)
            cwe_codes, frequencies = zip(*cwe_items)

            plt.figure(figsize=(12, 6))
            bars = plt.bar(cwe_codes, frequencies, color="skyblue")
            plt.xlabel("CWE Code")
            plt.ylabel("Frequency")
            plt.title(f"Frequency of CWEs in {repo}")
            plt.grid(True)
            plt.xticks(rotation=45, ha="right")
            for bar in bars:
                height = bar.get_height()
                plt.annotate(f'{height}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),
                             textcoords="offset points",
                             ha='center', va='bottom')
            plt.tight_layout()
            cwe_plot_path = os.path.join(results_folder, "cwe_frequency.png")
            plt.savefig(cwe_plot_path)
            plt.close()
            print(f"Saved CWE frequency plot for {repo} as {cwe_plot_path}")
        else:
            print(f"No CWE data found for repository {repo}.")

if __name__ == "__main__":
    main()