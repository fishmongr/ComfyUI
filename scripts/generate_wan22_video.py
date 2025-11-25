#!/usr/bin/env python3
"""
Generate Wan 2.2 i2v video from a source image using the API format template.

Usage:
    python scripts/generate_wan22_video.py <image_path> [options]

Example:
    python scripts/generate_wan22_video.py input/my-image.jpg --frames 25 --width 832 --height 1216
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional
import random

# ComfyUI API settings
DEFAULT_COMFYUI_URL = "http://localhost:8188"
API_PROMPT_TEMPLATE_PATH = "scripts/last_prompt_api_format.json"

def get_source_name(image_path: str) -> str:
    """Extract a clean source name from the image path."""
    filename = Path(image_path).stem
    # Remove common suffixes and clean up
    clean_name = filename.replace("sogni-photobooth-", "").replace("-raw", "")
    # Replace spaces and underscores with hyphens
    clean_name = clean_name.replace(" ", "-").replace("_", "-")
    return clean_name

def calculate_duration(frames: int, fps: int = 16) -> str:
    """Calculate video duration and format as string."""
    duration = frames / fps
    return f"{duration:.1f}s"

def load_api_prompt_template() -> Dict[str, Any]:
    """Load the API prompt template."""
    with open(API_PROMPT_TEMPLATE_PATH, 'r') as f:
        data = json.load(f)
    # The template is [1, client_id, {nodes}, {extra}, [outputs]]
    # We want index 2, which is the nodes dict
    return data[2]

def update_api_prompt(
    api_prompt: Dict[str, Any],
    image_path: str,
    frames: int,
    width: int,
    height: int,
    source_name: str,
    positive_prompt: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    settings: str = "4step_nosage"
) -> Dict[str, Any]:
    """
    Update API prompt with image path, prompts, and dynamic filename.
    
    Args:
        api_prompt: The API prompt dictionary to update
        image_path: Path to the source image
        frames: Number of frames to generate
        width: Video width
        height: Video height
        source_name: Clean name for the source image
        positive_prompt: Optional positive prompt text (node 93)
        negative_prompt: Optional negative prompt text (node 89)
        settings: Settings tag for filename
    """
    
    # Calculate duration
    duration = calculate_duration(frames)
    
    # Build filename pattern
    filename_pattern = (
        f"video/{source_name}_%width%x%height%_{frames}f_{duration}_{settings}_"
        "%year%%month%%day%_%hour%%minute%%second%"
    )
    
    # Generate a new random seed for node 86
    seed = random.randint(0, 2**48)
    
    # Update nodes
    # Use absolute path so ComfyUI can find the image
    abs_image_path = os.path.abspath(image_path)
    api_prompt["97"]["inputs"]["image"] = abs_image_path
    api_prompt["98"]["inputs"]["width"] = width
    api_prompt["98"]["inputs"]["height"] = height
    api_prompt["98"]["inputs"]["length"] = frames
    api_prompt["108"]["inputs"]["filename_prefix"] = filename_pattern
    api_prompt["86"]["inputs"]["noise_seed"] = seed
    
    # Update prompts if provided
    if positive_prompt is not None:
        api_prompt["93"]["inputs"]["text"] = positive_prompt
    
    if negative_prompt is not None:
        api_prompt["89"]["inputs"]["text"] = negative_prompt
    
    return api_prompt

def queue_prompt(prompt: Dict[str, Any], comfyui_url: str) -> Optional[str]:
    """Submit prompt to ComfyUI and return the prompt_id."""
    try:
        # Wrap the prompt in the expected format
        wrapped_prompt = {"prompt": prompt}
        data = json.dumps(wrapped_prompt).encode('utf-8')
        req = urllib.request.Request(
            f"{comfyui_url}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result.get("prompt_id")
    except urllib.error.HTTPError as e:
        # HTTP error - read the error response body for ComfyUI validation errors
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            print(f"[ERROR] ComfyUI rejected the prompt:")
            print(f"   Type: {error_data.get('type', 'unknown')}")
            print(f"   Message: {error_data.get('message', 'No message')}")
            if error_data.get('details'):
                print(f"   Details: {error_data['details']}")
            # Try to extract more specific validation errors
            if 'node_errors' in error_data:
                for node_id, errors in error_data['node_errors'].items():
                    print(f"   Node {node_id}: {errors}")
        except:
            print(f"[ERROR] HTTP Error {e.code}: {e.reason}")
            print(f"   Error response: {e.read().decode('utf-8', errors='ignore')}")
        return None
    except urllib.error.URLError as e:
        print(f"[ERROR] Error connecting to ComfyUI: {e}")
        print(f"   Make sure ComfyUI is running at {comfyui_url}")
        return None
    except Exception as e:
        print(f"[ERROR] Error queueing prompt: {e}")
        return None

def get_queue_status(comfyui_url: str) -> Dict[str, Any]:
    """Get the current queue status."""
    try:
        with urllib.request.urlopen(f"{comfyui_url}/queue") as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"[ERROR] Error getting queue status: {e}")
        return {}

def get_history(prompt_id: str, comfyui_url: str) -> Optional[Dict[str, Any]]:
    """Get the history for a specific prompt_id."""
    try:
        with urllib.request.urlopen(f"{comfyui_url}/history/{prompt_id}") as response:
            history = json.loads(response.read())
            return history.get(prompt_id)
    except Exception as e:
        return None

def wait_for_completion(prompt_id: str, comfyui_url: str, timeout: int = 600) -> bool:
    """Wait for the prompt to complete. Returns True if successful."""
    print(f"\nWaiting for generation to complete (timeout: {timeout}s)...")
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        # Check queue status
        queue_status = get_queue_status(comfyui_url)
        
        # Check if still in queue
        queue_running = queue_status.get("queue_running", [])
        queue_pending = queue_status.get("queue_pending", [])
        
        # Check if our prompt is running
        for item in queue_running:
            if len(item) >= 2 and item[1] == prompt_id:
                current_status = "[PROCESSING] Processing..."
                if current_status != last_status:
                    print(current_status)
                    last_status = current_status
                time.sleep(2)
                break
        else:
            # Not in running queue, check if completed
            history = get_history(prompt_id, comfyui_url)
            if history is not None:
                # Check for errors
                if "outputs" in history:
                    print("[OK] Generation completed!")
                    return True
                elif "error" in history:
                    print(f"[ERROR] Generation failed: {history['error']}")
                    return False
            
            # Check if still pending
            is_pending = any(len(item) >= 2 and item[1] == prompt_id for item in queue_pending)
            if is_pending:
                current_status = "[PENDING] Pending in queue..."
                if current_status != last_status:
                    print(current_status)
                    last_status = current_status
            
            time.sleep(2)
    
    print(f"[TIMEOUT] Timeout after {timeout}s")
    return False

def get_output_path(prompt_id: str, comfyui_url: str, source_name: str = None) -> Optional[str]:
    """Get the output video path from the history."""
    history = get_history(prompt_id, comfyui_url)
    if history and "outputs" in history:
        for node_id, output in history["outputs"].items():
            if "videos" in output:
                videos = output["videos"]
                if videos and len(videos) > 0:
                    video_info = videos[0]
                    subfolder = video_info.get("subfolder", "")
                    filename = video_info.get("filename", "")
                    output_dir = Path("output") / subfolder
                    return str(output_dir / filename)
    
    # Fallback: search for most recent video matching source name
    if source_name:
        video_dir = Path("output") / "video"
        if video_dir.exists():
            matching_videos = sorted(
                video_dir.glob(f"{source_name}*.mp4"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if matching_videos:
                return str(matching_videos[0])
    
    return None

def format_time(seconds: float) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {mins}m {secs:.1f}s"

def main():
    # Start overall timer
    script_start_time = time.time()
    timings = {}
    
    parser = argparse.ArgumentParser(
        description="Generate Wan 2.2 i2v video from an image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (25 frames, 832x1216)
  python scripts/generate_wan22_video.py input/my-image.jpg
  
  # Custom frame count (49 frames for 3s video)
  python scripts/generate_wan22_video.py input/my-image.jpg --frames 49
  
  # Custom resolution
  python scripts/generate_wan22_video.py input/my-image.jpg --width 1024 --height 1024 --frames 81
  
  # With custom prompts
  python scripts/generate_wan22_video.py input/my-image.jpg --positive "cinematic slow motion" --negative "blurry, distorted"
  
  # With automatic frame interpolation
  python scripts/generate_wan22_video.py input/my-image.jpg --interpolate film
  
  # Full example with all options
  python scripts/generate_wan22_video.py input/my-image.jpg --frames 81 --positive "smooth camera pan" --negative "blur" --interpolate film --crf 18
        """
    )
    
    parser.add_argument("image_path", help="Path to the source image")
    parser.add_argument("--frames", type=int, default=25, help="Number of frames to generate (default: 25)")
    parser.add_argument("--width", type=int, default=832, help="Video width (default: 832)")
    parser.add_argument("--height", type=int, default=1216, help="Video height (default: 1216)")
    parser.add_argument("--positive", type=str, default=None, 
                       help="Positive prompt (default: use template prompt)")
    parser.add_argument("--negative", type=str, default=None,
                       help="Negative prompt (default: use template prompt)")
    parser.add_argument("--settings", default="4step_nosage", help="Settings tag for filename (default: 4step_nosage)")
    parser.add_argument("--timeout", type=int, default=None, 
                       help="Timeout in seconds (default: auto - 600s for <80 frames, 720s for >=80 frames)")
    parser.add_argument("--url", default=DEFAULT_COMFYUI_URL, help=f"ComfyUI URL (default: {DEFAULT_COMFYUI_URL})")
    parser.add_argument(
        "--interpolate",
        choices=["film", "none"],
        default="none",
        help="Auto-interpolate output video to 32fps using FILM (default: none)"
    )
    parser.add_argument("--crf", type=int, default=18,
                       help="Quality for interpolated video: 10=near-lossless, 18=excellent, 23=high (default: 18)")
    
    args = parser.parse_args()
    
    # Set default timeout based on frame count if not specified
    if args.timeout is None:
        if args.frames >= 80:
            args.timeout = 720  # 12 minutes for long videos
        else:
            args.timeout = 600  # 10 minutes for short videos
    
    # Validate image path
    if not os.path.exists(args.image_path):
        print(f"[ERROR] Image not found: {args.image_path}")
        sys.exit(1)
    
    # Validate template path
    if not os.path.exists(API_PROMPT_TEMPLATE_PATH):
        print(f"[ERROR] API template not found: {API_PROMPT_TEMPLATE_PATH}")
        print("   Run ComfyUI and queue a prompt first to generate the template.")
        sys.exit(1)
    
    # Extract source name
    source_name = get_source_name(args.image_path)
    duration = calculate_duration(args.frames)
    
    print("=" * 70)
    print("Wan 2.2 i2v Video Generation")
    print("=" * 70)
    print(f"Source Image:  {args.image_path}")
    print(f"Source Name:   {source_name}")
    print(f"Resolution:    {args.width}x{args.height}")
    print(f"Frames:        {args.frames} ({duration} @ 16fps)")
    print(f"Settings:      {args.settings}")
    print(f"ComfyUI URL:   {args.url}")
    print(f"Timeout:       {args.timeout}s ({args.timeout//60}m {args.timeout%60}s)")
    if args.interpolate != "none":
        print(f"Interpolate:   {args.interpolate.upper()} to 32fps (CRF {args.crf})")
    print("=" * 70)
    
    # Load and update prompt
    print("\nLoading API template...")
    load_start = time.time()
    try:
        api_prompt = load_api_prompt_template()
        api_prompt = update_api_prompt(
            api_prompt,
            args.image_path,
            args.frames,
            args.width,
            args.height,
            source_name,
            args.positive,
            args.negative,
            args.settings
        )
    except Exception as e:
        print(f"[ERROR] Error loading/updating prompt: {e}")
        sys.exit(1)
    timings['template_load'] = time.time() - load_start
    
    # Queue the prompt
    print("Submitting to ComfyUI...")
    queue_start = time.time()
    prompt_id = queue_prompt(api_prompt, args.url)
    timings['queue_submit'] = time.time() - queue_start
    
    if not prompt_id:
        print("[ERROR] Failed to queue prompt")
        sys.exit(1)
    
    print(f"[OK] Prompt queued with ID: {prompt_id}")
    
    # Wait for completion
    print(f"\nWaiting for generation to complete (timeout: {args.timeout}s)...")
    generation_start = time.time()
    success = wait_for_completion(prompt_id, args.url, args.timeout)
    timings['generation'] = time.time() - generation_start
    
    if success:
        # Get output path
        output_path = get_output_path(prompt_id, args.url, source_name)
        if output_path:
            print(f"\n[SUCCESS] Video saved: {output_path}")
            print(f"   Generation time: {format_time(timings['generation'])}")
            
            # Check if file actually exists
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                print(f"   File size: {file_size:.2f} MB")
                
                # Auto-interpolate if requested
                if args.interpolate != "none":
                    print(f"\n{'='*70}")
                    print(f"Frame Interpolation: FILM (16fps -> 32fps)")
                    print(f"{'='*70}")
                    
                    interpolation_start = time.time()
                    
                    try:
                        # Build output filename to match what interpolate_pipeline creates
                        output_path_obj = Path(output_path)
                        base_name = output_path_obj.stem
                        if base_name.endswith('_'):
                            base_name = base_name[:-1]
                        interp_output = output_path_obj.parent / f"{base_name}_film_32fps_hq.mp4"
                        
                        print(f"\n[INFO] Running FILM interpolation in separate process...")
                        print(f"[INFO] (Will retry up to 3 times if GPU conflicts occur)")
                        
                        # Run interpolation in SEPARATE process to avoid CUDA conflicts
                        # Retry logic handles intermittent GPU initialization failures
                        interp_script = Path(__file__).parent / "interpolate_pipeline.py"
                        cmd = [
                            sys.executable,  # Use same Python interpreter
                            str(interp_script),
                            output_path,
                            "--method", "film",
                            "--crf", str(args.crf),
                            "--output", str(interp_output)
                        ]
                        
                        # Try up to 3 times with delays between attempts
                        max_retries = 3
                        success = False
                        
                        for attempt in range(1, max_retries + 1):
                            if attempt > 1:
                                wait_time = 2 * attempt  # 4s, 6s
                                print(f"\n[INFO] Retry attempt {attempt}/{max_retries} (waiting {wait_time}s for GPU to settle)...")
                                time.sleep(wait_time)
                            
                            result = subprocess.run(cmd, capture_output=False, text=True)
                            
                            if result.returncode == 0:
                                success = True
                                break
                            else:
                                if attempt < max_retries:
                                    print(f"[INFO] Attempt {attempt} failed, GPU may be busy, will retry...")
                        
                        if not success:
                            print(f"\n[ERROR] All {max_retries} attempts failed")
                        
                        timings['interpolation'] = time.time() - interpolation_start
                        
                        if success and os.path.exists(str(interp_output)):
                            interp_size = os.path.getsize(str(interp_output)) / (1024 * 1024)
                            print(f"\n[SUCCESS] FILM video: {interp_output}")
                            print(f"   Interpolation time: {format_time(timings['interpolation'])}")
                            print(f"   File size: {interp_size:.2f} MB ({interp_size/file_size:.1f}x)")
                        else:
                            if not success:
                                raise Exception("Interpolation subprocess failed (see output above)")
                            else:
                                raise Exception(f"Interpolated file not found at: {interp_output}")
                        
                    except KeyboardInterrupt:
                        print("\n\n[CANCELLED] Interrupted by user")
                        sys.exit(130)
                    except Exception as e:
                        timings['interpolation'] = time.time() - interpolation_start
                        print(f"\n[ERROR] FILM interpolation failed: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # Check for specific known errors
                        error_str = str(e)
                        if "ffmpeg" in error_str.lower():
                            print("\n[ERROR] FFmpeg is not installed or not in PATH!")
                            print("[INFO] Install with: winget install ffmpeg")
                            print("[INFO] Then restart your terminal and try again")
                        
                        print(f"\n[INFO] Original video still available: {output_path}")
                        print(f"[INFO] To retry interpolation manually, run:")
                        print(f'      python scripts/interpolate_pipeline.py "{output_path}" --method film --crf {args.crf}')
                        sys.exit(1)  # Fail loudly
                
            else:
                print(f"[WARNING] Warning: Output file not found at expected path")
        else:
            print("\n[WARNING] Generation completed but couldn't determine output path")
            print("   Check the ComfyUI output folder manually")
        
        # Print timing summary
        total_time = time.time() - script_start_time
        print(f"\n{'='*70}")
        print("TIMING SUMMARY")
        print(f"{'='*70}")
        print(f"Template Load:      {format_time(timings.get('template_load', 0))}")
        print(f"Queue Submit:       {format_time(timings.get('queue_submit', 0))}")
        print(f"Video Generation:   {format_time(timings.get('generation', 0))}")
        if 'interpolation' in timings:
            print(f"FILM Interpolation: {format_time(timings['interpolation'])}")
        print(f"{'-'*70}")
        print(f"Total Time:         {format_time(total_time)}")
        print(f"{'='*70}\n")
        
        sys.exit(0)
    else:
        print("\n[ERROR] Generation failed or timed out")
        total_time = time.time() - script_start_time
        print(f"Total time before failure: {format_time(total_time)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
