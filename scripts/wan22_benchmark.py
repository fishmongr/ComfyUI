#!/usr/bin/env python3
"""
Automated benchmark script for Wan 2.2 i2v video generation.

This script systematically tests different configurations and generates
performance reports.

Usage:
    python scripts/wan22_benchmark.py [options]

Example:
    python scripts/wan22_benchmark.py --test-frames 25,49,81 --output benchmarks/rtx5090_test1.csv
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Default settings
DEFAULT_COMFYUI_URL = "http://localhost:8188"
DEFAULT_TEST_IMAGE = "input/sogni-photobooth-my-polar-bear-baby-raw.jpg"
DEFAULT_OUTPUT_DIR = "benchmarks"

def get_system_stats(comfyui_url: str) -> Dict[str, Any]:
    """Get current system stats from ComfyUI."""
    try:
        with urllib.request.urlopen(f"{comfyui_url}/system_stats") as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"[WARNING] Could not fetch system stats: {e}")
        return {}

def run_generation_test(
    image_path: str,
    frames: int,
    width: int,
    height: int,
    settings: str,
    comfyui_url: str,
    timeout: int = 600
) -> Dict[str, Any]:
    """
    Run a single generation test and return metrics.
    
    Returns dict with:
        - success: bool
        - duration: float (seconds)
        - vram_used: float (MB)
        - vram_total: float (MB)
        - error: str (if failed)
    """
    print(f"\n{'='*70}")
    print(f"Testing: {frames} frames @ {width}x{height} ({settings})")
    print(f"{'='*70}")
    
    # Get initial system stats
    start_stats = get_system_stats(comfyui_url)
    start_time = time.time()
    
    # Run generation using our script
    cmd = [
        sys.executable,
        "scripts/generate_wan22_video.py",
        image_path,
        "--frames", str(frames),
        "--width", str(width),
        "--height", str(height),
        "--settings", settings,
        "--url", comfyui_url,
        "--timeout", str(timeout)
    ]
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    duration = time.time() - start_time
    
    # Get final system stats
    end_stats = get_system_stats(comfyui_url)
    
    # Extract metrics
    metrics = {
        "success": result.returncode == 0,
        "duration": duration,
        "frames": frames,
        "width": width,
        "height": height,
        "settings": settings,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add VRAM info
    if end_stats and "devices" in end_stats:
        for device in end_stats["devices"]:
            if device.get("type") == "cuda":
                metrics["vram_used_mb"] = device.get("vram_used", 0) / (1024 * 1024)
                metrics["vram_total_mb"] = device.get("vram_total", 0) / (1024 * 1024)
                metrics["vram_percent"] = (metrics["vram_used_mb"] / metrics["vram_total_mb"] * 100) if metrics["vram_total_mb"] > 0 else 0
                break
    
    if not metrics["success"]:
        metrics["error"] = result.stderr if result.stderr else "Unknown error"
        print(f"[ERROR] Test failed: {metrics['error']}")
    else:
        print(f"[OK] Test completed in {duration:.2f}s")
        if "vram_percent" in metrics:
            print(f"     VRAM: {metrics['vram_used_mb']:.0f}MB / {metrics['vram_total_mb']:.0f}MB ({metrics['vram_percent']:.1f}%)")
    
    return metrics

def save_results(results: List[Dict[str, Any]], output_path: str):
    """Save benchmark results to CSV."""
    if not results:
        print("[WARNING] No results to save")
        return
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Get all possible field names
    fieldnames = set()
    for result in results:
        fieldnames.update(result.keys())
    fieldnames = sorted(fieldnames)
    
    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n[OK] Results saved to: {output_path}")

def generate_summary_report(results: List[Dict[str, Any]], output_dir: str):
    """Generate a human-readable summary report."""
    if not results:
        return
    
    report_path = Path(output_dir) / "summary_report.txt"
    
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("Wan 2.2 i2v Benchmark Summary Report\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {len(results)}\n")
        f.write(f"Successful: {sum(1 for r in results if r['success'])}\n")
        f.write(f"Failed: {sum(1 for r in results if not r['success'])}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("Individual Test Results\n")
        f.write("=" * 70 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"Test {i}: {result['frames']} frames @ {result['width']}x{result['height']}\n")
            f.write(f"  Settings: {result['settings']}\n")
            f.write(f"  Status: {'SUCCESS' if result['success'] else 'FAILED'}\n")
            f.write(f"  Duration: {result['duration']:.2f}s\n")
            
            if "vram_used_mb" in result:
                f.write(f"  VRAM: {result['vram_used_mb']:.0f}MB / {result['vram_total_mb']:.0f}MB ({result['vram_percent']:.1f}%)\n")
            
            if not result['success'] and "error" in result:
                f.write(f"  Error: {result['error'][:200]}\n")
            
            f.write("\n")
        
        # Calculate statistics for successful tests
        successful = [r for r in results if r['success']]
        if successful:
            f.write("=" * 70 + "\n")
            f.write("Performance Statistics (Successful Tests Only)\n")
            f.write("=" * 70 + "\n\n")
            
            durations = [r['duration'] for r in successful]
            f.write(f"Duration:\n")
            f.write(f"  Average: {sum(durations)/len(durations):.2f}s\n")
            f.write(f"  Min: {min(durations):.2f}s\n")
            f.write(f"  Max: {max(durations):.2f}s\n\n")
            
            if all("vram_percent" in r for r in successful):
                vram_pcts = [r['vram_percent'] for r in successful]
                f.write(f"VRAM Usage:\n")
                f.write(f"  Average: {sum(vram_pcts)/len(vram_pcts):.1f}%\n")
                f.write(f"  Min: {min(vram_pcts):.1f}%\n")
                f.write(f"  Max: {max(vram_pcts):.1f}%\n")
    
    print(f"[OK] Summary report saved to: {report_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Automated benchmark for Wan 2.2 i2v",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--image", default=DEFAULT_TEST_IMAGE, help=f"Test image path (default: {DEFAULT_TEST_IMAGE})")
    parser.add_argument("--test-frames", default="25,49,81", help="Comma-separated frame counts to test (default: 25,49,81)")
    parser.add_argument("--width", type=int, default=832, help="Video width (default: 832)")
    parser.add_argument("--height", type=int, default=1216, help="Video height (default: 1216)")
    parser.add_argument("--settings", default="4step_nosage", help="Settings tag (default: 4step_nosage)")
    parser.add_argument("--output", default=None, help="Output CSV path (default: benchmarks/benchmark_TIMESTAMP.csv)")
    parser.add_argument("--url", default=DEFAULT_COMFYUI_URL, help=f"ComfyUI URL (default: {DEFAULT_COMFYUI_URL})")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per test in seconds (default: 600)")
    
    args = parser.parse_args()
    
    # Validate image
    if not os.path.exists(args.image):
        print(f"[ERROR] Image not found: {args.image}")
        sys.exit(1)
    
    # Parse frame counts
    try:
        frame_counts = [int(f.strip()) for f in args.test_frames.split(",")]
    except ValueError:
        print(f"[ERROR] Invalid frame counts: {args.test_frames}")
        sys.exit(1)
    
    # Generate output path
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"{DEFAULT_OUTPUT_DIR}/benchmark_{timestamp}.csv"
    
    output_dir = str(Path(args.output).parent)
    
    print("=" * 70)
    print("Wan 2.2 i2v Benchmark Suite")
    print("=" * 70)
    print(f"Image: {args.image}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Frame counts: {frame_counts}")
    print(f"Settings: {args.settings}")
    print(f"Output: {args.output}")
    print(f"ComfyUI URL: {args.url}")
    print("=" * 70)
    
    # Run tests
    results = []
    for frames in frame_counts:
        try:
            result = run_generation_test(
                args.image,
                frames,
                args.width,
                args.height,
                args.settings,
                args.url,
                args.timeout
            )
            results.append(result)
        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Benchmark interrupted by user")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            results.append({
                "success": False,
                "frames": frames,
                "width": args.width,
                "height": args.height,
                "settings": args.settings,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Save results
    if results:
        save_results(results, args.output)
        generate_summary_report(results, output_dir)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Benchmark Complete")
    print("=" * 70)
    successful = sum(1 for r in results if r['success'])
    print(f"Tests completed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print("=" * 70)

if __name__ == "__main__":
    main()


