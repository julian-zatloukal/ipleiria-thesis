#!/usr/bin/env python3
"""
Script to parse transient data files (voltage and current) into separate dataset files.
Creates a subfolder 'transient_parsed' and splits the data by each dataset header.
"""

import os
import re
from pathlib import Path

def parse_transient_data(input_file: str, output_dir: str) -> dict:
    """
    Parse a combined transient data file and split into individual dataset files.
    
    Args:
        input_file: Path to the input data file
        output_dir: Directory to store the parsed files
        
    Returns:
        Dictionary with dataset names and their line counts
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    datasets = {}
    current_dataset = None
    current_lines = []
    current_name = None
    
    with open(input_file, 'r') as f:
        for line in f:
            # Check if this is a header line (starts with "time")
            if line.startswith('time'):
                # Save previous dataset if exists
                if current_name and current_lines:
                    save_dataset(output_dir, current_name, current_lines)
                    datasets[current_name] = len(current_lines) - 1  # Exclude header
                
                # Parse new dataset name from header
                parts = line.strip().split()
                if len(parts) >= 2:
                    current_name = parts[1]
                else:
                    current_name = "unknown"
                
                current_lines = [line]
            else:
                current_lines.append(line)
        
        # Save the last dataset
        if current_name and current_lines:
            save_dataset(output_dir, current_name, current_lines)
            datasets[current_name] = len(current_lines) - 1  # Exclude header
    
    return datasets


def save_dataset(output_dir: str, name: str, lines: list) -> str:
    """
    Save a dataset to a file.
    
    Args:
        output_dir: Directory to save the file
        name: Dataset name (used for filename)
        lines: Lines of data including header
        
    Returns:
        Path to the saved file
    """
    # Clean the name for use as filename
    # Format: Tran1.TRAN.VRL -> tran1_vrl.dat
    clean_name = name.replace('.TRAN.', '_').replace('.', '_').lower()
    filename = f"{clean_name}.dat"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.writelines(lines)
    
    print(f"  Saved: {filename} ({len(lines) - 1} data points)")
    return filepath


def main():
    # Define paths
    script_dir = Path(__file__).parent
    output_dir = script_dir / "transient_parsed"
    
    # Input files: separate voltage and current files
    voltage_file = script_dir / "data_pa_transient_voltage.dat"
    current_file = script_dir / "data_pa_transient_current.dat"
    
    print("=" * 60)
    print("Transient Data Parser")
    print("=" * 60)
    print(f"\nVoltage file: {voltage_file}")
    print(f"Current file: {current_file}")
    print(f"Output directory: {output_dir}\n")
    
    all_datasets = {}
    
    # Parse voltage file
    if voltage_file.exists():
        print("Parsing voltage datasets...\n")
        voltage_datasets = parse_transient_data(str(voltage_file), str(output_dir))
        all_datasets.update(voltage_datasets)
    else:
        print(f"Warning: Voltage file not found: {voltage_file}")
    
    # Parse current file
    if current_file.exists():
        print("\nParsing current datasets...\n")
        current_datasets = parse_transient_data(str(current_file), str(output_dir))
        all_datasets.update(current_datasets)
    else:
        print(f"Warning: Current file not found: {current_file}")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"\nTotal datasets extracted: {len(all_datasets)}")
    print(f"Total data points: {sum(all_datasets.values())}")
    print(f"\nDatasets:")
    
    # Group by type
    voltage_datasets = {k: v for k, v in all_datasets.items() if 'V' in k and 'I_' not in k}
    current_datasets = {k: v for k, v in all_datasets.items() if 'I_' in k or 'i' in k.lower()}
    
    print("\n  Voltage signals:")
    for name, count in voltage_datasets.items():
        print(f"    - {name}: {count} points")
    
    print("\n  Current signals:")
    for name, count in current_datasets.items():
        print(f"    - {name}: {count} points")
    
    print(f"\nOutput directory: {output_dir}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
