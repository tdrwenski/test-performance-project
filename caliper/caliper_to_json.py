#!/usr/bin/env python3
"""
Generic Caliper to GitHub benchmark converter
Automatically detects what Caliper has collected and converts to GitHub format
"""
import json
import sys
import subprocess
import os

def discover_caliper_attributes(cali_file):
    """
    Discover what attributes are available in a .cali file
    Returns a dict with timing attributes and their event types
    """
    try:
        # Get basic info about the .cali file
        result = subprocess.run(['cali-query', '-t', cali_file],
                              capture_output=True, text=True, check=True)

        # Look for common timing attributes in the output
        timing_attrs = []
        context_attrs = []

        lines = result.stdout.split('\n')
        if len(lines) > 1:  # Skip header
            # Parse header to find available columns
            header = lines[0].split()
            for col in header:
                if 'time' in col.lower() and 'duration' in col.lower():
                    timing_attrs.append(col)
                elif col in ['function', 'region', 'phase', 'loop']:
                    context_attrs.append(col)

        return {
            'timing_attrs': timing_attrs,
            'context_attrs': context_attrs,
            'has_data': len(lines) > 2  # More than just header
        }

    except subprocess.CalledProcessError as e:
        print(f"Error running cali-query: {e}", file=sys.stderr)
        return {'timing_attrs': [], 'context_attrs': [], 'has_data': False}

def build_generic_query(timing_attrs, context_attrs):
    """
    Build a CalQL query based on available attributes
    """
    if not timing_attrs or not context_attrs:
        return None

    # Use the first available timing attribute and context attribute
    timing_attr = timing_attrs[0]
    context_attr = context_attrs[0]

    # Build query to get average timing per context
    query = f"""
    SELECT {context_attr}, avg({timing_attr}), count(), sum({timing_attr})
    WHERE event.end#{context_attr}
    GROUP BY {context_attr}
    FORMAT json(pretty)
    """

    return query.strip()

def run_caliper_query(cali_file, query):
    """
    Run a CalQL query and return the JSON results
    """
    try:
        result = subprocess.run(['cali-query', '-q', query, cali_file],
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running query: {e}", file=sys.stderr)
        print(f"Query was: {query}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        print(f"Output was: {result.stdout}", file=sys.stderr)
        return None

def convert_to_github_format(caliper_data, context_attr, timing_attr):
    """
    Convert Caliper JSON to GitHub benchmark format using native units
    """
    github_benchmarks = []

    for entry in caliper_data:
        # Get the context name (function, region, etc.)
        context_name = entry.get(context_attr, 'unknown').strip()

        # Get timing value - try different possible keys
        timing_value = None
        for key in [f'avg#{timing_attr}', f'sum#{timing_attr}', timing_attr]:
            if key in entry:
                timing_value = entry[key]
                break

        if timing_value is None:
            continue

        # Determine unit from timing attribute name
        # Caliper typically uses nanoseconds for time.inclusive.duration
        if 'duration' in timing_attr.lower():
            unit = "nanoseconds"
        elif 'time' in timing_attr.lower():
            unit = "nanoseconds"  # Default assumption
        else:
            unit = "units"  # Generic fallback

        # Create GitHub benchmark entry
        benchmark_entry = {
            "name": f"Caliper {context_attr.title()} - {context_name}".strip(),
            "unit": unit,
            "value": timing_value
        }

        # Add extra info if available
        extra_info = []
        if 'count' in entry:
            extra_info.append(f"Invocations: {entry['count']}")
        if f'sum#{timing_attr}' in entry and f'avg#{timing_attr}' in entry:
            extra_info.append(f"Total time: {entry[f'sum#{timing_attr}']} {unit}")

        if extra_info:
            benchmark_entry["extra"] = "\\n".join(extra_info).strip()

        github_benchmarks.append(benchmark_entry)

    return github_benchmarks

def process_caliper_file(cali_file, verbose=False):
    """
    Process a .cali file and convert to GitHub benchmark format
    """
    if verbose:
        print(f"Analyzing {cali_file}...", file=sys.stderr)

    # Discover what's in the file
    attrs = discover_caliper_attributes(cali_file)

    if not attrs['has_data']:
        print(f"No data found in {cali_file}", file=sys.stderr)
        return []

    if verbose:
        print(f"Found timing attributes: {attrs['timing_attrs']}", file=sys.stderr)
        print(f"Found context attributes: {attrs['context_attrs']}", file=sys.stderr)

    # Build appropriate query
    query = build_generic_query(attrs['timing_attrs'], attrs['context_attrs'])
    if not query:
        print("Could not build query - no suitable attributes found", file=sys.stderr)
        return []

    if verbose:
        print(f"Using query: {query}", file=sys.stderr)

    # Run the query
    caliper_data = run_caliper_query(cali_file, query)
    if not caliper_data:
        return []

    # Convert to GitHub format
    context_attr = attrs['context_attrs'][0]
    timing_attr = attrs['timing_attrs'][0]

    return convert_to_github_format(caliper_data, context_attr, timing_attr)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generic_caliper_converter.py <caliper_file.cali> [--verbose]")
        print("  --verbose: show detailed processing info")
        sys.exit(1)

    cali_file = sys.argv[1]
    verbose = False

    # Parse additional arguments
    for arg in sys.argv[2:]:
        if arg == "--verbose":
            verbose = True

    if not os.path.exists(cali_file):
        print(f"File not found: {cali_file}", file=sys.stderr)
        sys.exit(1)

    # Process the file
    github_data = process_caliper_file(cali_file, verbose)

    if not github_data:
        print("No benchmark data could be extracted", file=sys.stderr)
        sys.exit(1)

    # Output JSON with no trailing whitespace
    json_output = json.dumps(github_data, indent=2, separators=(',', ': '))
    print(json_output.rstrip())

if __name__ == "__main__":
    main()
