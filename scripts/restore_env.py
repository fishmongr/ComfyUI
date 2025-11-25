#!/usr/bin/env python3
"""
Restore environment configuration from a saved snapshot.
Applies environment variables from a previous working configuration.
"""

import json
import os
import sys
from pathlib import Path


def load_environment_snapshot(snapshot_file='environment_snapshot.json'):
    """Load environment snapshot"""
    snapshot_path = Path(__file__).parent / snapshot_file
    
    if not snapshot_path.exists():
        print(f"Error: Snapshot file not found: {snapshot_path}")
        return None
    
    with open(snapshot_path, 'r') as f:
        snapshot = json.load(f)
    
    return snapshot


def restore_environment(snapshot):
    """Restore environment variables from snapshot"""
    if not snapshot:
        return False
    
    env_vars = snapshot.get('environment_variables', {})
    
    print("Restoring environment variables:")
    for var, value in env_vars.items():
        if value != 'NOT_SET':
            os.environ[var] = value
            print(f"  {var}={value}")
    
    print("\nEnvironment restored from snapshot:")
    print(f"  Timestamp: {snapshot.get('timestamp')}")
    print(f"  PyTorch: {snapshot.get('pytorch_info', {}).get('pytorch_version')}")
    print(f"  CUDA: {snapshot.get('pytorch_info', {}).get('cuda_version')}")
    
    return True


def generate_bat_script(snapshot, output_file='restore_env.bat'):
    """Generate a .bat script to set environment variables"""
    env_vars = snapshot.get('environment_variables', {})
    
    output_path = Path(__file__).parent / output_file
    
    with open(output_path, 'w') as f:
        f.write("@echo off\n")
        f.write("REM Auto-generated environment restore script\n")
        f.write(f"REM Generated from snapshot: {snapshot.get('timestamp')}\n\n")
        
        for var, value in env_vars.items():
            if value != 'NOT_SET':
                f.write(f"set {var}={value}\n")
        
        f.write("\necho Environment variables restored from snapshot\n")
    
    print(f"\nBatch script generated: {output_path}")
    return output_path


if __name__ == '__main__':
    snapshot = load_environment_snapshot()
    if snapshot:
        restore_environment(snapshot)
        generate_bat_script(snapshot)
    else:
        sys.exit(1)

