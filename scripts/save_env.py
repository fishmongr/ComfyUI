#!/usr/bin/env python3
"""
Environment Snapshot Tool for Wan 2.2 Optimization
Captures current system state for reproducibility
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run command and return output, or None if failed"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        return f"Error: {str(e)}"

def get_gpu_info():
    """Get NVIDIA GPU information"""
    gpu_info = {}
    
    # Basic GPU info
    query = "name,driver_version,memory.total,power.limit,temperature.gpu,utilization.gpu,utilization.memory"
    cmd = f'nvidia-smi --query-gpu={query} --format=csv,noheader,nounits'
    output = run_command(cmd)
    
    if output and not output.startswith("Error"):
        parts = [p.strip() for p in output.split(',')]
        gpu_info = {
            'name': parts[0] if len(parts) > 0 else None,
            'driver_version': parts[1] if len(parts) > 1 else None,
            'vram_total_mb': parts[2] if len(parts) > 2 else None,
            'power_limit_w': parts[3] if len(parts) > 3 else None,
            'temperature_c': parts[4] if len(parts) > 4 else None,
            'gpu_utilization_pct': parts[5] if len(parts) > 5 else None,
            'memory_utilization_pct': parts[6] if len(parts) > 6 else None,
        }
    
    # Clock speeds
    clocks_cmd = 'nvidia-smi --query-gpu=clocks.gr,clocks.mem --format=csv,noheader,nounits'
    clocks = run_command(clocks_cmd)
    if clocks and not clocks.startswith("Error"):
        parts = [p.strip() for p in clocks.split(',')]
        gpu_info['clock_graphics_mhz'] = parts[0] if len(parts) > 0 else None
        gpu_info['clock_memory_mhz'] = parts[1] if len(parts) > 1 else None
    
    return gpu_info

def get_pytorch_info():
    """Get PyTorch and CUDA information"""
    try:
        import torch
        return {
            'pytorch_version': torch.__version__,
            'cuda_available': torch.cuda.is_available(),
            'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
            'cudnn_version': torch.backends.cudnn.version() if torch.cuda.is_available() else None,
            'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
            'gpu_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
    except ImportError:
        return {'error': 'PyTorch not available'}

def get_environment_vars():
    """Get performance-related environment variables"""
    relevant_vars = [
        'PYTORCH_CUDA_ALLOC_CONF',
        'CUDA_LAUNCH_BLOCKING',
        'TORCH_COMPILE',
        'TORCH_COMPILE_MODE',
        'OMP_NUM_THREADS',
        'CUDA_MODULE_LOADING',
        'CUDA_VISIBLE_DEVICES',
        'PYTHONPATH',
    ]
    
    return {var: os.environ.get(var) for var in relevant_vars}

def get_system_info():
    """Get system information"""
    power_scheme = run_command('powercfg /getactivescheme')
    
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'os_release': platform.release(),
        'python_version': sys.version,
        'power_scheme': power_scheme,
        'timestamp': datetime.now().isoformat(),
    }

def save_snapshot(output_file='environment_snapshot.json'):
    """Save complete environment snapshot"""
    snapshot = {
        'system': get_system_info(),
        'gpu': get_gpu_info(),
        'pytorch': get_pytorch_info(),
        'environment_variables': get_environment_vars(),
    }
    
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"Environment snapshot saved to: {output_path.absolute()}")
    print(f"\nGPU: {snapshot['gpu'].get('name', 'Unknown')}")
    print(f"PyTorch: {snapshot['pytorch'].get('pytorch_version', 'Not installed')}")
    print(f"CUDA: {snapshot['pytorch'].get('cuda_version', 'N/A')}")
    
    return snapshot

if __name__ == '__main__':
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'environment_snapshot.json'
    save_snapshot(output_file)
