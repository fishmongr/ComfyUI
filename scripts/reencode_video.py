#!/usr/bin/env python3
"""
Re-encode video with better compression to reduce file size

This script re-encodes videos using ffmpeg with optimized settings
to achieve approximately 2x file size for 2x frames.

Usage:
    python scripts/reencode_video.py input.mp4 [output.mp4]
    
    # Re-encode FILM output
    python scripts/reencode_video.py output/video/polar-bear_..._film_32fps.mp4
    
    # Batch re-encode
    python scripts/reencode_video.py output/video/*_film_32fps.mp4
"""

import os
import sys
import subprocess
import argparse
import glob
from pathlib import Path
from typing import Optional

def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_bitrate(input_path: str) -> Optional[int]:
    """Get the bitrate of the input video using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=bit_rate',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        bitrate = int(result.stdout.strip())
        return bitrate
    except:
        return None


def reencode_video(input_path: str, output_path: Optional[str] = None, target_bitrate: Optional[str] = None) -> bool:
    """
    Re-encode video with better compression
    
    Args:
        input_path: Input video path
        output_path: Output video path (default: adds _reencoded suffix)
        target_bitrate: Target bitrate (e.g., '2M', '1500k'). If None, auto-calculate.
    
    Returns:
        True if successful
    """
    if not os.path.exists(input_path):
        print(f"[ERROR] Input file not found: {input_path}")
        return False
    
    # Check ffmpeg
    if not check_ffmpeg():
        print("[ERROR] ffmpeg not found. Please install ffmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        return False
    
    # Determine output path
    if output_path is None:
        input_path_obj = Path(input_path)
        output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_reencoded{input_path_obj.suffix}")
    
    # Get input size
    input_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    
    print(f"\n[INFO] Re-encoding: {input_path}")
    print(f"[INFO] Input size: {input_size_mb:.2f} MB")
    
    # Get input bitrate if available
    if target_bitrate is None:
        input_bitrate = get_video_bitrate(input_path)
        if input_bitrate:
            # Use same bitrate as input for maintaining quality
            target_bitrate = f"{input_bitrate}"
            print(f"[INFO] Using input bitrate: {input_bitrate / 1000:.0f} kb/s")
        else:
            # Default to reasonable bitrate
            target_bitrate = "2M"
            print(f"[INFO] Using default bitrate: {target_bitrate}")
    
    # Build ffmpeg command
    # Using H.264 with CRF (Constant Rate Factor) for better quality/size ratio
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',           # H.264 codec
        '-preset', 'medium',         # Encoding speed (medium is good balance)
        '-crf', '23',                # Quality (18-28, lower = better quality)
        '-movflags', '+faststart',   # Enable streaming
        '-pix_fmt', 'yuv420p',       # Compatibility
        '-y',                         # Overwrite output
        output_path
    ]
    
    print(f"[INFO] Encoding with H.264 (CRF 23)...")
    
    try:
        # Run ffmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Get output size
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        size_ratio = output_size_mb / input_size_mb
        
        print(f"[SUCCESS] Output size: {output_size_mb:.2f} MB ({size_ratio:.2f}x)")
        print(f"[SUCCESS] Saved to: {output_path}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ffmpeg failed: {e}")
        if e.stderr:
            print(f"[ERROR] {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Re-encode video with better compression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Re-encode single video
  python scripts/reencode_video.py output/video/my-video_film_32fps.mp4
  
  # Specify output path
  python scripts/reencode_video.py input.mp4 output.mp4
  
  # Batch re-encode
  python scripts/reencode_video.py output/video/*_film_32fps.mp4
  
  # With custom bitrate
  python scripts/reencode_video.py input.mp4 --bitrate 2M
        """
    )
    
    parser.add_argument("input", help="Input video file(s). Supports wildcards.")
    parser.add_argument("output", nargs='?', help="Output video file (optional)")
    parser.add_argument("--bitrate", help="Target bitrate (e.g., 2M, 1500k)")
    parser.add_argument("--replace", action="store_true", 
                       help="Replace original file (use with caution!)")
    
    args = parser.parse_args()
    
    # Collect input files
    if '*' in args.input:
        files = glob.glob(args.input)
    elif os.path.isfile(args.input):
        files = [args.input]
    else:
        print(f"[ERROR] Input not found: {args.input}")
        return 1
    
    if not files:
        print(f"[ERROR] No files found matching: {args.input}")
        return 1
    
    # Check if output specified for multiple files
    if len(files) > 1 and args.output:
        print("[ERROR] Cannot specify output path for multiple input files")
        return 1
    
    print("=" * 70)
    print("Video Re-encoding with H.264")
    print("=" * 70)
    print(f"[INFO] Found {len(files)} file(s) to process")
    
    success_count = 0
    fail_count = 0
    
    for file in files:
        try:
            # Determine output path
            if args.replace:
                # Create temp file, then replace
                temp_output = file + ".temp.mp4"
                if reencode_video(file, temp_output, args.bitrate):
                    os.replace(temp_output, file)
                    print(f"[INFO] Replaced original file: {file}")
                    success_count += 1
                else:
                    if os.path.exists(temp_output):
                        os.remove(temp_output)
                    fail_count += 1
            else:
                output = args.output if args.output else None
                if reencode_video(file, output, args.bitrate):
                    success_count += 1
                else:
                    fail_count += 1
                    
        except Exception as e:
            print(f"[ERROR] Failed to process {file}: {e}")
            fail_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Completed: {success_count} successful, {fail_count} failed")
    print("=" * 70)
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())




