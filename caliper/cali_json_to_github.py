#!/usr/bin/env python3
"""
Convert cali-query JSON output to GitHub benchmark format
"""
import json
import sys
import os

def convert_to_github_format(cali_data):
    """
    Convert cali-query JSON to GitHub benchmark format
    Expected input format:
    [{"path": "function_name", "avg#time.duration.ns": 12345}]
    
    GitHub format:
    [{"name": "Function - function_name", "unit": "nanoseconds", "value": 12345}]
    """
    github_benchmarks = []

    for entry in cali_data:
        # Get function name from path
        path = entry.get('path', 'unknown')

        # Get timing value - look for avg timing first, then other timing keys
        timing_value = None
        timing_key = None

        for key in entry:
            if 'avg#time.duration' in key:
                timing_value = entry[key]
                timing_key = key
                break
            elif 'time.duration' in key:
                timing_value = entry[key]
                timing_key = key
                break

        if timing_value is None:
            continue

        # Determine unit from the key
        unit = "nanoseconds"  # Default
        if '.ns' in timing_key:
            unit = "nanoseconds"
        elif '.us' in timing_key:
            unit = "microseconds"
        elif '.ms' in timing_key:
            unit = "milliseconds"
        elif '.s' in timing_key:
            unit = "seconds"

        # Create GitHub benchmark entry
        benchmark_entry = {
            "name": f"Caliper Function - {path}",
            "unit": unit,
            "value": timing_value
        }

        # Add extra metadata if available
        extra_info = []
        if 'region.count' in entry:
            extra_info.append(f"Calls: {entry['region.count']}")

        if extra_info:
            benchmark_entry["extra"] = " | ".join(extra_info)

        github_benchmarks.append(benchmark_entry)

    return github_benchmarks

def main():
    if len(sys.argv) < 2:
        print("Usage: python cali_json_to_github.py <cali_query_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"File not found: {json_file}", file=sys.stderr)
        sys.exit(1)

    # Read the JSON file
    try:
        with open(json_file, 'r') as f:
            cali_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert to GitHub format
    github_data = convert_to_github_format(cali_data)

    if not github_data:
        print("No benchmark data could be extracted", file=sys.stderr)
        sys.exit(1)

    # Output JSON
    json_output = json.dumps(github_data, indent=2, separators=(',', ': '))
    print(json_output.rstrip())

if __name__ == "__main__":
    main()