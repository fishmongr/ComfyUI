#!/usr/bin/env python3
"""
Benchmark Frame Interpolation Methods
Compare RIFE vs FILM on existing 16fps videos

This script processes videos with both methods and generates a comparison report
including processing time, output quality metrics, and file sizes.

Usage:
    # Benchmark all videos in a directory
    python scripts/benchmark_interpolation.py output/video/

    # Benchmark specific videos
    python scripts/benchmark_interpolation.py output/video/polar-bear_*.mp4

    # Save detailed report
    python scripts/benchmark_interpolation.py output/video/ --report benchmarks/interpolation_report.txt

Author: ComfyUI Frame Interpolation
Date: 2025-11-24
"""

import os
import sys
import time
import glob
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add ComfyUI to path
COMFYUI_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(COMFYUI_ROOT))

try:
    import cv2
    from interpolate_video import VideoInterpolator, get_output_filename, get_video_info
except ImportError as e:
    print(f"[ERROR] Missing required dependency: {e}")
    sys.exit(1)


def benchmark_video(
    input_path: str,
    method: str,
    output_dir: Optional[str] = None
) -> Dict:
    """
    Benchmark a single video with specified method

    Returns dict with:
        - success: bool
        - method: str
        - input_path: str
        - output_path: str
        - processing_time: float
        - input_size_mb: float
        - output_size_mb: float
        - input_fps: float
        - output_fps: float
        - input_frames: int
        - output_frames: int
    """
    result = {
        'success': False,
        'method': method,
        'input_path': input_path,
        'output_path': None,
        'processing_time': 0.0,
        'input_size_mb': 0.0,
        'output_size_mb': 0.0,
        'input_fps': 0.0,
        'output_fps': 0.0,
        'input_frames': 0,
        'output_frames': 0,
        'error': None
    }

    try:
        # Get input info
        input_info = get_video_info(input_path)
        result['input_fps'] = input_info.get('fps', 0)
        result['input_frames'] = input_info.get('frames', 0)
        result['input_size_mb'] = os.path.getsize(input_path) / (1024 * 1024)

        # Get output path
        output_path = get_output_filename(input_path, method, output_dir)
        result['output_path'] = output_path

        # Check if already exists
        if os.path.exists(output_path):
            print(f"[SKIP] {method.upper()} output already exists: {output_path}")
            # Get existing output info
            output_info = get_video_info(output_path)
            result['output_fps'] = output_info.get('fps', 0)
            result['output_frames'] = output_info.get('frames', 0)
            result['output_size_mb'] = os.path.getsize(output_path) / (1024 * 1024)
            result['processing_time'] = 0.0  # Unknown
            result['success'] = True
            return result

        # Process video
        print(f"\n[BENCHMARK] Processing with {method.upper()}...")
        start_time = time.time()

        interpolator = VideoInterpolator(method=method)
        success = interpolator.process_video(input_path, output_path, target_fps=32)

        end_time = time.time()
        processing_time = end_time - start_time

        result['processing_time'] = processing_time
        result['success'] = success

        if success:
            # Get output info
            output_info = get_video_info(output_path)
            result['output_fps'] = output_info.get('fps', 0)
            result['output_frames'] = output_info.get('frames', 0)
            result['output_size_mb'] = os.path.getsize(output_path) / (1024 * 1024)

            print(f"[SUCCESS] {method.upper()} completed in {processing_time:.1f}s")
        else:
            result['error'] = "Processing failed"
            print(f"[ERROR] {method.upper()} processing failed")

    except Exception as e:
        result['error'] = str(e)
        print(f"[ERROR] {method.upper()} benchmark failed: {e}")

    return result


def compare_methods(input_path: str, output_dir: Optional[str] = None) -> Dict:
    """
    Compare RIFE and FILM on the same video

    Returns comparison dict with results for both methods
    """
    print(f"\n{'='*70}")
    print(f"Benchmarking: {Path(input_path).name}")
    print(f"{'='*70}")

    # Benchmark with both methods
    rife_result = benchmark_video(input_path, "rife", output_dir)
    film_result = benchmark_video(input_path, "film", output_dir)

    # Create comparison
    comparison = {
        'input_path': input_path,
        'input_info': {
            'fps': rife_result['input_fps'],
            'frames': rife_result['input_frames'],
            'size_mb': rife_result['input_size_mb']
        },
        'rife': rife_result,
        'film': film_result
    }

    # Print comparison
    print(f"\n{'='*70}")
    print("Comparison Summary")
    print(f"{'='*70}")
    print(f"Input: {Path(input_path).name}")
    print(f"  FPS: {comparison['input_info']['fps']:.1f}")
    print(f"  Frames: {comparison['input_info']['frames']}")
    print(f"  Size: {comparison['input_info']['size_mb']:.2f} MB")

    print(f"\nRIFE:")
    print(f"  Success: {rife_result['success']}")
    if rife_result['success']:
        print(f"  Processing Time: {rife_result['processing_time']:.1f}s")
        print(f"  Output Frames: {rife_result['output_frames']}")
        print(f"  Output Size: {rife_result['output_size_mb']:.2f} MB")
        if rife_result['processing_time'] > 0:
            fps_processed = rife_result['input_frames'] / rife_result['processing_time']
            print(f"  Speed: {fps_processed:.1f} fps")
    else:
        print(f"  Error: {rife_result.get('error', 'Unknown')}")

    print(f"\nFILM:")
    print(f"  Success: {film_result['success']}")
    if film_result['success']:
        print(f"  Processing Time: {film_result['processing_time']:.1f}s")
        print(f"  Output Frames: {film_result['output_frames']}")
        print(f"  Output Size: {film_result['output_size_mb']:.2f} MB")
        if film_result['processing_time'] > 0:
            fps_processed = film_result['input_frames'] / film_result['processing_time']
            print(f"  Speed: {fps_processed:.1f} fps")
    else:
        print(f"  Error: {film_result.get('error', 'Unknown')}")

    # Winner
    if rife_result['success'] and film_result['success']:
        if rife_result['processing_time'] > 0 and film_result['processing_time'] > 0:
            if rife_result['processing_time'] < film_result['processing_time']:
                speedup = film_result['processing_time'] / rife_result['processing_time']
                print(f"\n🏆 RIFE is {speedup:.1f}x faster")
            elif film_result['processing_time'] < rife_result['processing_time']:
                speedup = rife_result['processing_time'] / film_result['processing_time']
                print(f"\n🏆 FILM is {speedup:.1f}x faster")
            else:
                print(f"\n🏆 Both methods took the same time")

    return comparison


def generate_report(comparisons: List[Dict], report_path: str):
    """Generate a detailed benchmark report"""
    report_dir = Path(report_path).parent
    report_dir.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("Frame Interpolation Benchmark Report\n")
        f.write("=" * 70 + "\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Videos Tested: {len(comparisons)}\n")
        f.write("\n")

        # Summary statistics
        total_rife_time = sum(c['rife']['processing_time'] for c in comparisons if c['rife']['success'])
        total_film_time = sum(c['film']['processing_time'] for c in comparisons if c['film']['success'])
        rife_success = sum(1 for c in comparisons if c['rife']['success'])
        film_success = sum(1 for c in comparisons if c['film']['success'])

        f.write("Summary Statistics\n")
        f.write("-" * 70 + "\n")
        f.write(f"RIFE: {rife_success}/{len(comparisons)} successful, {total_rife_time:.1f}s total\n")
        f.write(f"FILM: {film_success}/{len(comparisons)} successful, {total_film_time:.1f}s total\n")
        f.write("\n")

        # Per-video details
        f.write("Detailed Results\n")
        f.write("-" * 70 + "\n")

        for i, comp in enumerate(comparisons, 1):
            f.write(f"\n{i}. {Path(comp['input_path']).name}\n")
            f.write(f"   Input: {comp['input_info']['frames']} frames @ {comp['input_info']['fps']:.1f}fps, "
                   f"{comp['input_info']['size_mb']:.2f} MB\n")

            # RIFE
            rife = comp['rife']
            f.write(f"   RIFE: ")
            if rife['success']:
                f.write(f"{rife['processing_time']:.1f}s, {rife['output_frames']} frames, "
                       f"{rife['output_size_mb']:.2f} MB\n")
            else:
                f.write(f"FAILED - {rife.get('error', 'Unknown')}\n")

            # FILM
            film = comp['film']
            f.write(f"   FILM: ")
            if film['success']:
                f.write(f"{film['processing_time']:.1f}s, {film['output_frames']} frames, "
                       f"{film['output_size_mb']:.2f} MB\n")
            else:
                f.write(f"FAILED - {film.get('error', 'Unknown')}\n")

    print(f"\n[SUCCESS] Report saved to: {report_path}")

    # Also save JSON version
    json_path = Path(report_path).with_suffix('.json')
    with open(json_path, 'w') as f:
        json.dump(comparisons, f, indent=2)
    print(f"[SUCCESS] JSON data saved to: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark RIFE vs FILM Frame Interpolation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Benchmark all videos in directory
  python scripts/benchmark_interpolation.py output/video/

  # Benchmark specific videos
  python scripts/benchmark_interpolation.py output/video/polar-bear_*.mp4

  # Save detailed report
  python scripts/benchmark_interpolation.py output/video/ --report benchmarks/interpolation_comparison.txt
        """
    )

    parser.add_argument(
        "input",
        help="Input video file(s) or directory. Supports wildcards (*.mp4)"
    )

    parser.add_argument(
        "--output",
        help="Output directory for interpolated videos (default: same as input)"
    )

    parser.add_argument(
        "--report",
        help="Path to save benchmark report (default: benchmarks/interpolation_benchmark.txt)",
        default="benchmarks/interpolation_benchmark.txt"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of videos to process (for quick testing)"
    )

    args = parser.parse_args()

    # Print header
    print("=" * 70)
    print("Frame Interpolation Benchmark - RIFE vs FILM")
    print("=" * 70)

    # Collect input files
    input_path = Path(args.input)
    if '*' in str(input_path):
        files = glob.glob(str(input_path))
    elif input_path.is_dir():
        files = list(input_path.glob("*.mp4"))
    elif input_path.is_file():
        files = [str(input_path)]
    else:
        print(f"[ERROR] Input not found: {args.input}")
        return 1

    # Filter out already interpolated videos
    files = [f for f in files if "_rife_32fps" not in f and "_film_32fps" not in f]

    if not files:
        print(f"[ERROR] No videos found to benchmark")
        return 1

    # Apply limit
    if args.limit:
        files = files[:args.limit]

    print(f"[INFO] Found {len(files)} video(s) to benchmark")

    # Benchmark each video
    comparisons = []
    for i, file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {Path(file).name}")
        comparison = compare_methods(file, args.output)
        comparisons.append(comparison)

    # Generate report
    generate_report(comparisons, args.report)

    # Final summary
    print("\n" + "=" * 70)
    print("Benchmark Complete")
    print("=" * 70)
    print(f"Videos tested: {len(comparisons)}")
    print(f"Report saved to: {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())




