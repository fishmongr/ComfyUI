#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Wan 2.2 s2v (sound-to-video) from audio using the API format template.

This script generates videos synchronized to audio using the Wan 2.2 s2v model.

Usage:
    python scripts/generate_wan22_sound_video.py <audio_path> [options]

Example:
    python scripts/generate_wan22_sound_video.py input/music.mp3 --ref-image input/album-art.jpg --frames 305
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

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ComfyUI API settings
DEFAULT_COMFYUI_URL = "http://localhost:8188"
API_PROMPT_TEMPLATE_PATH = "scripts/last_prompt_api_format_s2v.json"

# Supported audio formats (loaded via PyAV)
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.opus', '.wma']

def get_source_name(audio_path: str) -> str:
    """Extract a clean source name from the audio path."""
    filename = Path(audio_path).stem
    # Remove common suffixes and clean up
    clean_name = filename.replace(" ", "-").replace("_", "-")
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
    audio_path: str,
    ref_image_path: Optional[str],
    frames: int,
    width: int,
    height: int,
    source_name: str,
    positive_prompt: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    settings: str = "s2v",
    audio_start_time: float = 0.0,
    audio_duration: Optional[float] = None
) -> Dict[str, Any]:
    """
    Update API prompt with audio path, prompts, and dynamic filename.
    
    Args:
        api_prompt: The API prompt dictionary to update
        audio_path: Path to the audio file
        ref_image_path: Optional path to reference image
        frames: Number of frames to generate
        width: Video width
        height: Video height
        source_name: Clean name for the source
        positive_prompt: Optional positive prompt text (node 93)
        negative_prompt: Optional negative prompt text (node 89)
        settings: Settings tag for filename
        audio_start_time: Start time in audio file (seconds)
        audio_duration: Duration to use from audio (None = auto-calculate from frames)
    """
    
    # Calculate duration
    duration = calculate_duration(frames)
    
    # Auto-calculate audio duration if not specified
    if audio_duration is None:
        audio_duration = frames / 16.0  # 16 fps
    
    # Build filename pattern
    has_ref = "with_ref" if ref_image_path else "no_ref"
    filename_pattern = (
        f"video/{source_name}_%width%x%height%_{frames}f_{duration}_{has_ref}_{settings}_"
        "%year%%month%%day%_%hour%%minute%%second%"
    )
    
    # Generate a new random seed for node 86
    seed = random.randint(0, 2**48)
    
    # Update audio path (node 119)
    abs_audio_path = os.path.abspath(audio_path)
    api_prompt["119"]["inputs"]["audio"] = abs_audio_path
    
    # Add audio trimming node if start time or duration specified
    if audio_start_time > 0 or audio_duration is not None:
        if "121" not in api_prompt:
            api_prompt["121"] = {
                "inputs": {
                    "audio": ["119", 0],
                    "start_index": audio_start_time,
                    "duration": audio_duration
                },
                "class_type": "TrimAudioDuration",
                "_meta": {
                    "title": "Trim Audio"
                }
            }
        else:
            api_prompt["121"]["inputs"]["start_index"] = audio_start_time
            api_prompt["121"]["inputs"]["duration"] = audio_duration
        
        # Update audio encoder to use trimmed audio
        api_prompt["122"]["inputs"]["audio"] = ["121", 0]
        
        # Update CreateVideo to use trimmed audio too (node 94)
        api_prompt["94"]["inputs"]["audio"] = ["121", 0]
    else:
        # Use audio directly
        api_prompt["122"]["inputs"]["audio"] = ["119", 0]
        
        # CreateVideo uses original audio (node 94)
        api_prompt["94"]["inputs"]["audio"] = ["119", 0]
        
        # Remove trim node if it exists
        if "121" in api_prompt:
            del api_prompt["121"]
    
    # Update reference image if provided
    if ref_image_path:
        abs_ref_image_path = os.path.abspath(ref_image_path)
        api_prompt["97"]["inputs"]["image"] = abs_ref_image_path
        api_prompt["98"]["inputs"]["ref_image"] = ["97", 0]
    else:
        # Remove ref_image if it exists
        if "ref_image" in api_prompt["98"]["inputs"]:
            del api_prompt["98"]["inputs"]["ref_image"]
    
    # Update node parameters
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

def wait_for_completion(prompt_id: str, comfyui_url: str, timeout: int = 1200) -> bool:
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
                    output_dir = Path("output") / subfolder if subfolder else Path("output")
                    full_path = output_dir / filename
                    if full_path.exists():
                        return str(full_path)
    
    # Fallback: search for most recent video file
    video_dir = Path("output") / "video"
    if video_dir.exists():
        # First try exact source name match
        if source_name:
            matching_videos = sorted(
                video_dir.glob(f"{source_name}*.mp4"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if matching_videos:
                return str(matching_videos[0])
        
        # Fallback: just get the most recent MP4
        all_videos = sorted(
            video_dir.glob("*.mp4"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        if all_videos:
            return str(all_videos[0])
    
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
        description="Generate Wan 2.2 s2v video from audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (77 frames, 832x1216)
  python scripts/generate_wan22_sound_video.py input/music.mp3
  
  # With reference image
  python scripts/generate_wan22_sound_video.py input/music.mp3 --ref-image input/album-art.jpg
  
  # Custom frame count (305 frames for ~19s video)
  python scripts/generate_wan22_sound_video.py input/music.mp3 --frames 305
  
  # Use specific part of audio (start at 30s, use 5s duration)
  python scripts/generate_wan22_sound_video.py input/long-song.mp3 --audio-start 30 --audio-duration 5 --frames 81
  
  # Custom resolution
  python scripts/generate_wan22_sound_video.py input/music.mp3 --width 1024 --height 1024 --frames 161
  
  # With custom prompts
  python scripts/generate_wan22_sound_video.py input/music.mp3 --positive "dynamic dance movements" --negative "static, boring"
  
  # With FILM interpolation (16fps -> 32fps)
  python scripts/generate_wan22_sound_video.py input/music.mp3 --frames 77 --interpolate film
        """
    )
    
    parser.add_argument("audio_path", help="Path to the audio file (wav/mp3/m4a/flac/ogg/etc)")
    parser.add_argument("--ref-image", type=str, default=None,
                       help="Path to reference image (optional - provides visual style/subject)")
    parser.add_argument("--frames", type=int, default=77, help="Number of frames to generate (default: 77 for ~4.8s)")
    parser.add_argument("--audio-start", type=float, default=0.0,
                       help="Start time in audio file in seconds (default: 0.0)")
    parser.add_argument("--audio-duration", type=float, default=None,
                       help="Duration of audio to use in seconds (default: auto-calculate from frames)")
    parser.add_argument("--width", type=int, default=832, help="Video width (default: 832)")
    parser.add_argument("--height", type=int, default=1216, help="Video height (default: 1216)")
    parser.add_argument("--positive", type=str, default=None, 
                       help="Positive prompt (default: use template prompt)")
    parser.add_argument("--negative", type=str, default=None,
                       help="Negative prompt (default: use template prompt)")
    parser.add_argument("--settings", default="s2v", help="Settings tag for filename (default: s2v)")
    parser.add_argument("--timeout", type=int, default=None, 
                       help="Timeout in seconds (default: auto based on frames)")
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
        if args.frames >= 200:
            args.timeout = 1800  # 30 minutes for very long videos
        elif args.frames >= 100:
            args.timeout = 1200  # 20 minutes for long videos
        else:
            args.timeout = 900  # 15 minutes for standard videos
    
    # Validate audio path
    if not os.path.exists(args.audio_path):
        print(f"[ERROR] Audio file not found: {args.audio_path}")
        sys.exit(1)
    
    # Check audio format
    audio_ext = Path(args.audio_path).suffix.lower()
    if audio_ext not in SUPPORTED_AUDIO_FORMATS:
        print(f"[WARNING] Audio format '{audio_ext}' may not be supported")
        print(f"   Supported formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}")
        print(f"   Attempting to load anyway...")
    
    # Validate reference image if provided
    if args.ref_image and not os.path.exists(args.ref_image):
        print(f"[ERROR] Reference image not found: {args.ref_image}")
        sys.exit(1)
    
    # Validate template path
    if not os.path.exists(API_PROMPT_TEMPLATE_PATH):
        print(f"[ERROR] API template not found: {API_PROMPT_TEMPLATE_PATH}")
        print("   Template should be at scripts/last_prompt_api_format_s2v.json")
        sys.exit(1)
    
    # Extract source name
    source_name = get_source_name(args.audio_path)
    duration = calculate_duration(args.frames)
    
    print("=" * 70)
    print("Wan 2.2 S2V (Sound-to-Video) Generation")
    print("=" * 70)
    print(f"Audio File:    {args.audio_path}")
    if args.ref_image:
        print(f"Reference Img: {args.ref_image}")
    else:
        print(f"Reference Img: None (audio-only generation)")
    print(f"Audio Format:  {audio_ext.upper()}")
    if args.audio_start > 0 or args.audio_duration:
        print(f"Audio Segment: {args.audio_start}s to {args.audio_start + (args.audio_duration or (args.frames/16))}s")
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
            args.audio_path,
            args.ref_image,
            args.frames,
            args.width,
            args.height,
            source_name,
            args.positive,
            args.negative,
            args.settings,
            args.audio_start,
            args.audio_duration
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
                        # Build output filename
                        output_path_obj = Path(output_path)
                        base_name = output_path_obj.stem
                        if base_name.endswith('_'):
                            base_name = base_name[:-1]
                        interp_output = output_path_obj.parent / f"{base_name}_film_32fps_hq.mp4"
                        
                        print(f"\n[INFO] Running FILM interpolation in separate process...")
                        print(f"[INFO] (Will retry up to 3 times if GPU conflicts occur)")
                        
                        # Run interpolation in SEPARATE process
                        interp_script = Path(__file__).parent / "interpolate_pipeline.py"
                        cmd = [
                            sys.executable,
                            str(interp_script),
                            output_path,
                            "--method", "film",
                            "--crf", str(args.crf),
                            "--output", str(interp_output)
                        ]
                        
                        # Try up to 3 times
                        max_retries = 3
                        success = False
                        
                        for attempt in range(1, max_retries + 1):
                            if attempt > 1:
                                wait_time = 2 * attempt
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
                        
                        print(f"\n[INFO] Original video still available: {output_path}")
                        print(f"[INFO] To retry interpolation manually, run:")
                        print(f'      python scripts/interpolate_pipeline.py "{output_path}" --method film --crf {args.crf}')
                        sys.exit(1)
                
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

