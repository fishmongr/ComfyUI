#!/usr/bin/env python3
"""
High-Quality Frame Interpolation Pipeline
Avoids double compression by saving/loading frame sequences

This pipeline:
1. Saves ComfyUI output as PNG sequence (lossless)
2. Interpolates frames
3. Encodes once to final video

Usage:
    # Process existing video by extracting frames first
    python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film

    # Or specify frame sequence directory directly
    python scripts/interpolate_pipeline.py --frames path/to/frames/ --fps 16 --method film
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import Optional, Tuple
import tempfile

COMFYUI_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(COMFYUI_ROOT))

try:
    import cv2
    import numpy as np
except ImportError as e:
    print(f"[ERROR] Missing required dependency: {e}")
    print(f"[ERROR] Install with: pip install opencv-python numpy")
    if __name__ == "__main__":
        sys.exit(1)
    else:
        raise  # Re-raise when imported as module

# tqdm is optional - only used for progress bars in standalone mode
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# Import torch early to avoid DLL initialization errors after GPU usage
try:
    import torch
    from PIL import Image
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None
    Image = None


def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False


def extract_frames_lossless(video_path: str, output_dir: str) -> Tuple[int, float]:
    """Extract frames from video as PNG (lossless)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video info
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    print(f"[INFO] Extracting {total_frames} frames as PNG...", flush=True)
    
    # Extract as PNG with ffmpeg
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-f', 'image2',
        '-c:v', 'png',  # PNG codec (lossless)
        os.path.join(output_dir, 'frame_%05d.png'),
        '-y'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Frame extraction failed: {result.stderr}")
        return 0, fps
    
    # Count extracted frames
    frame_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
    
    return len(frame_files), fps


def interpolate_frames_from_dir(input_dir: str, method: str = "film"):
    """Interpolate frames from a directory of PNG images"""
    try:
        if not HAS_TORCH:
            print("[ERROR] PyTorch not available - cannot run interpolation")
            return None
        
        import sys
        import numpy as np
        
        # Add ComfyUI paths
        comfy_path = os.path.abspath(os.path.dirname(__file__) + "/..")
        sys.path.insert(0, comfy_path)
        
        # Get sorted list of frames
        frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
        
        if len(frame_files) < 2:
            print("[ERROR] Need at least 2 frames to interpolate")
            return None
        
        print(f"[INFO] Interpolating {len(frame_files)} frames using {method.upper()}...", flush=True)
        
        # Use ComfyUI's FILM model - no fallbacks
        if method.lower() == "film":
            # Add custom_nodes path for importing
            custom_nodes_path = os.path.join(comfy_path, "custom_nodes", "ComfyUI-Frame-Interpolation")
            if custom_nodes_path not in sys.path:
                sys.path.insert(0, custom_nodes_path)
            
            from vfi_models.film import FILM_VFI
            from vfi_utils import load_file_from_github_release
            
            MODEL_TYPE = "film"
            ckpt_name = "film_net_fp32.pt"
            model_path = load_file_from_github_release(MODEL_TYPE, ckpt_name)
            model = torch.jit.load(model_path, map_location='cpu')
            
            # Load all frames as tensors
            frames = []
            for i, frame_file in enumerate(frame_files):
                img = Image.open(os.path.join(input_dir, frame_file))
                img_np = np.array(img).astype(np.float32) / 255.0
                frames.append(torch.from_numpy(img_np))
            
            # Stack into batch tensor
            frames_tensor = torch.stack(frames)
            
            # Adjust cache clearing based on frame count
            cache_clear_freq = 30 if len(frames) > 100 else 10
            
            # Run FILM interpolation
            film_vfi = FILM_VFI()
            result = film_vfi.vfi(
                ckpt_name=ckpt_name,
                frames=frames_tensor,
                multiplier=2,
                clear_cache_after_n_frames=cache_clear_freq
            )
            
            # Encode directly to video (skip saving frames to disk)
            output_frames = result[0]  # FILM_VFI returns (IMAGE,)
            print(f"[INFO] Generated {len(output_frames)} interpolated frames", flush=True)
            
            # Return frames tensor for direct encoding
            return output_frames
        
        else:
            print(f"[ERROR] Unsupported interpolation method: {method}")
            return None
    
    except KeyboardInterrupt:
        print("\n[CANCELLED] Interpolation interrupted by user", flush=True)
        raise
    except Exception as e:
        print(f"\n[ERROR] Interpolation failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None


def encode_frames_to_video(
    frames_dir: str,
    output_path: str,
    fps: float,
    crf: int = 18,
    preset: str = "medium"
) -> bool:
    """Encode PNG frames to video with single compression pass"""
    
    # Get first frame to determine resolution
    frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    if not frame_files:
        print("[ERROR] No frames found")
        return False
    
    print(f"[INFO] Encoding {len(frame_files)} frames to video @ {fps}fps...", flush=True)
    
    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', os.path.join(frames_dir, 'interp_%05d.png'),
        '-c:v', 'libx264',
        '-preset', preset,
        '-crf', str(crf),
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-y',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] Encoding failed: {result.stderr}")
        return False
    
    # Show results
    output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    duration = len(frame_files) / fps
    
    print(f"[SUCCESS] Video saved: {output_path}", flush=True)
    print(f"[SUCCESS] {duration:.1f}s @ {fps}fps, {output_size_mb:.2f} MB", flush=True)
    
    return True


def encode_tensors_to_video(
    frames_tensor,
    output_path: str,
    fps: float,
    crf: int = 18,
    preset: str = "medium"
) -> bool:
    """Encode frames directly from tensor to video (avoids disk writes)"""
    
    num_frames = len(frames_tensor)
    print(f"[INFO] Encoding {num_frames} frames to video @ {fps}fps (direct from memory)...", flush=True)
    
    # Use opencv to write directly via FFmpeg pipe
    import cv2
    
    # Get frame dimensions from first frame
    first_frame = (frames_tensor[0].cpu().numpy() * 255).astype(np.uint8)
    height, width = first_frame.shape[:2]
    
    # Create FFmpeg process with pipe input
    cmd = [
        'ffmpeg',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',  # Read from stdin
        '-c:v', 'libx264',
        '-preset', preset,
        '-crf', str(crf),
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        '-y',
        output_path
    ]
    
    try:
        # Redirect stderr to DEVNULL to avoid pipe buffer deadlock
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL
        )
        
        # Stream frames to FFmpeg
        for idx, frame_tensor in enumerate(frames_tensor):
            if idx % 50 == 0 and idx > 0:
                print(f"[INFO]   Encoding progress: {idx}/{num_frames} frames...", flush=True)
            
            frame_np = (frame_tensor.cpu().numpy() * 255).astype(np.uint8)
            process.stdin.write(frame_np.tobytes())
        
        # Close stdin and wait for process to finish
        process.stdin.close()
        process.wait()
        
        if process.returncode != 0:
            print(f"[ERROR] Encoding failed with exit code: {process.returncode}")
            return False
        
        # Show results
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        duration = num_frames / fps
        
        print(f"[SUCCESS] Video saved: {output_path}", flush=True)
        print(f"[SUCCESS] {duration:.1f}s @ {fps}fps, {output_size_mb:.2f} MB", flush=True)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Direct encoding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_pipeline(
    input_path: str,
    output_path: str,
    method: str = "film",
    crf: int = 18,
    keep_frames: bool = False
) -> bool:
    """
    Complete pipeline: Extract → Interpolate → Encode (direct from memory)
    """
    if not check_ffmpeg():
        print("[ERROR] ffmpeg is required for this pipeline")
        return False
    
    print("=" * 70)
    print("High-Quality Frame Interpolation Pipeline")
    print("=" * 70)
    print(f"Input: {input_path}")
    print(f"Method: {method.upper()}")
    print(f"Quality: CRF {crf}")
    print("=" * 70)
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix='comfyui_hq_interp_')
    frames_in = os.path.join(temp_dir, 'frames_in')
    
    try:
        # Step 1: Extract frames (lossless)
        frame_count, input_fps = extract_frames_lossless(input_path, frames_in)
        if frame_count == 0:
            return False
        
        # Step 2: Interpolate (returns tensor, no disk writes)
        interpolated_tensor = interpolate_frames_from_dir(frames_in, method)
        if interpolated_tensor is None:
            return False
        
        # Step 3: Encode directly from tensor (single compression pass, no disk I/O)
        output_fps = input_fps * 2
        success = encode_tensors_to_video(interpolated_tensor, output_path, output_fps, crf)
        
        return success
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="High-Quality Frame Interpolation (Avoids Double Compression)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard: Process existing video with high quality
  python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film

  # Maximum quality (near-lossless, CRF 10)
  python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film --crf 10

  # Fast encoding (lower quality, CRF 23)
  python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method rife --crf 23 --preset fast

  # Keep extracted frames for inspection
  python scripts/interpolate_pipeline.py output/video/my-video.mp4 --method film --keep-frames

Quality Settings (CRF):
  0-10:  Near-lossless (very large files)
  15-18: Excellent quality (recommended for archival)
  19-23: High quality (recommended for distribution)
  24-28: Good quality (smaller files)

Preset (encoding speed):
  veryslow: Best compression, slowest
  slow:     Great compression
  medium:   Good balance (default)
  fast:     Faster encoding, larger files
  ultrafast: Very fast, much larger files
        """
    )
    
    parser.add_argument("input", help="Input video file")
    parser.add_argument("--method", choices=["rife", "film"], default="film",
                       help="Interpolation method (default: film)")
    parser.add_argument("--output", help="Output video path (optional)")
    parser.add_argument("--crf", type=int, default=18,
                       help="Quality: 0=lossless, 18=excellent, 23=high (default: 18)")
    parser.add_argument("--preset", choices=["ultrafast", "fast", "medium", "slow", "veryslow"],
                       default="medium", help="Encoding speed (default: medium)")
    parser.add_argument("--keep-frames", action="store_true",
                       help="Keep extracted frames after processing")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        return 1
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input)
        base_name = input_path.stem
        if base_name.endswith('_'):
            base_name = base_name[:-1]
        output_path = input_path.parent / f"{base_name}_{args.method}_32fps_hq.mp4"
    
    # Check if already exists
    if os.path.exists(output_path):
        print(f"[WARNING] Output already exists: {output_path}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            return 0
    
    # Process
    success = process_pipeline(
        args.input,
        str(output_path),
        method=args.method,
        crf=args.crf,
        keep_frames=args.keep_frames
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())



