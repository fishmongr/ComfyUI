#!/usr/bin/env python3
"""
Frame Interpolation using FFmpeg for proper video encoding
Doubles 16fps videos to 32fps using RIFE or FILM with optimized compression

This version extracts frames, interpolates them, and re-encodes with ffmpeg
for proper compression (achieving ~2x file size for 2x frames).

Usage:
    python scripts/interpolate_video_ffmpeg.py input.mp4 --method rife
    python scripts/interpolate_video_ffmpeg.py input.mp4 --method film
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import Optional
import tempfile

# Add ComfyUI to path
COMFYUI_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(COMFYUI_ROOT))

try:
    import cv2
    import torch
    import numpy as np
    from tqdm import tqdm
except ImportError as e:
    print(f"[ERROR] Missing required dependency: {e}")
    sys.exit(1)


def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_frames(video_path: str, output_dir: str) -> tuple[int, float, int, int]:
    """
    Extract frames from video using ffmpeg
    Returns: (frame_count, fps, width, height)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video info
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    # Extract frames with ffmpeg (faster and better quality)
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-qscale:v', '1',  # High quality
        os.path.join(output_dir, 'frame_%04d.png'),
        '-y'
    ]
    
    print(f"[INFO] Extracting {frame_count} frames...")
    subprocess.run(cmd, capture_output=True, check=True)
    
    return frame_count, fps, width, height


def interpolate_frames(input_dir: str, output_dir: str, method: str = "rife"):
    """
    Interpolate frames between extracted frames
    """
    from interpolate_video import VideoInterpolator
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of input frames
    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    
    if len(frame_files) < 2:
        print("[ERROR] Not enough frames to interpolate")
        return False
    
    print(f"[INFO] Interpolating {len(frame_files)} frames with {method.upper()}...")
    
    # Initialize interpolator
    interpolator = VideoInterpolator(method=method)
    interpolator.load_model()
    
    # Read all frames
    frames = []
    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(input_dir, frame_file))
        frames.append(frame)
    
    # Interpolate and save
    output_idx = 1
    with tqdm(total=len(frames), desc=f"{method.upper()} Interpolation") as pbar:
        for i in range(len(frames)):
            # Save original frame
            output_file = os.path.join(output_dir, f'interp_{output_idx:04d}.png')
            cv2.imwrite(output_file, frames[i])
            output_idx += 1
            
            # Interpolate between this and next frame
            if i < len(frames) - 1:
                mid_frame = interpolator.interpolate_frame(frames[i], frames[i + 1], 0.5)
                output_file = os.path.join(output_dir, f'interp_{output_idx:04d}.png')
                cv2.imwrite(output_file, mid_frame)
                output_idx += 1
            
            pbar.update(1)
    
    print(f"[SUCCESS] Generated {output_idx - 1} interpolated frames")
    return True


def encode_video(frames_dir: str, output_path: str, fps: float, width: int, height: int, input_path: str):
    """
    Encode frames into video with proper compression
    """
    print(f"[INFO] Encoding video at {fps}fps with H.264...")
    
    # Get input file bitrate to match quality
    input_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    
    # Use CRF for better quality control
    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', os.path.join(frames_dir, 'interp_%04d.png'),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',  # Constant quality (18-28, lower = better)
        '-movflags', '+faststart',
        '-pix_fmt', 'yuv420p',
        '-y',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] ffmpeg encoding failed: {result.stderr}")
        return False
    
    # Report results
    output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    size_ratio = output_size_mb / input_size_mb
    
    print(f"[SUCCESS] Video encoded")
    print(f"[SUCCESS] Input size: {input_size_mb:.2f} MB")
    print(f"[SUCCESS] Output size: {output_size_mb:.2f} MB ({size_ratio:.1f}x)")
    print(f"[SUCCESS] Saved to: {output_path}")
    
    return True


def process_video_ffmpeg(input_path: str, output_path: str, method: str = "rife") -> bool:
    """
    Process video with ffmpeg for proper compression
    """
    if not check_ffmpeg():
        print("[ERROR] ffmpeg not found. Please install ffmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        print("  Mac: brew install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        return False
    
    print(f"\n[INFO] Processing: {input_path}")
    print(f"[INFO] Method: {method.upper()}")
    print(f"[INFO] Using ffmpeg for optimal compression")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix='comfyui_interp_')
    frames_in_dir = os.path.join(temp_dir, 'frames_in')
    frames_out_dir = os.path.join(temp_dir, 'frames_out')
    
    try:
        # Step 1: Extract frames
        frame_count, fps, width, height = extract_frames(input_path, frames_in_dir)
        
        # Step 2: Interpolate
        success = interpolate_frames(frames_in_dir, frames_out_dir, method)
        if not success:
            return False
        
        # Step 3: Encode video at 2x fps
        output_fps = fps * 2
        success = encode_video(frames_out_dir, output_path, output_fps, width, height, input_path)
        
        return success
        
    finally:
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def get_output_filename(input_path: str, method: str, output_dir: Optional[str] = None) -> str:
    """Generate output filename following naming convention"""
    input_path = Path(input_path)
    base_name = input_path.stem
    
    if base_name.endswith('_'):
        base_name = base_name[:-1]
    
    new_name = f"{base_name}_{method}_32fps.mp4"
    
    if output_dir:
        output_path = Path(output_dir) / new_name
    else:
        output_path = input_path.parent / new_name
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Frame Interpolation with FFmpeg (16fps -> 32fps)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with RIFE (recommended)
  python scripts/interpolate_video_ffmpeg.py output/video/my-video.mp4 --method rife
  
  # Process with FILM
  python scripts/interpolate_video_ffmpeg.py output/video/my-video.mp4 --method film
  
  # Both methods
  python scripts/interpolate_video_ffmpeg.py output/video/my-video.mp4 --method both
  
Note: This version uses ffmpeg for proper compression, achieving ~2x file size for 2x frames.
        """
    )
    
    parser.add_argument("input", help="Input video file")
    parser.add_argument("--method", choices=["rife", "film", "both"], default="rife",
                       help="Interpolation method (default: rife)")
    parser.add_argument("--output", help="Output directory (default: same as input)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        return 1
    
    # Check if already interpolated
    if "_rife_32fps" in args.input or "_film_32fps" in args.input:
        print(f"[SKIP] Video already interpolated: {args.input}")
        return 0
    
    print("=" * 70)
    print("ComfyUI Frame Interpolation with FFmpeg")
    print("=" * 70)
    
    methods = ["rife", "film"] if args.method == "both" else [args.method]
    
    success_count = 0
    fail_count = 0
    
    for method in methods:
        output_path = get_output_filename(args.input, method, args.output)
        
        if os.path.exists(output_path):
            print(f"[SKIP] Output already exists: {output_path}")
            continue
        
        try:
            if process_video_ffmpeg(args.input, output_path, method):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"[ERROR] Failed: {e}")
            fail_count += 1
    
    print("\n" + "=" * 70)
    print(f"Completed: {success_count} successful, {fail_count} failed")
    print("=" * 70)
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())




