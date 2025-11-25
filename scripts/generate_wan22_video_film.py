#!/usr/bin/env python3
"""
Generate Wan 2.2 i2v video with PNG output + automatic FILM interpolation

This script:
1. Generates video using PNG frame sequence (no compression)
2. Automatically runs FILM interpolation (16fps -> 32fps)
3. Encodes final video with high quality (CRF 18)

Usage:
    python scripts/generate_wan22_video_film.py <image_path> [options]

Example:
    python scripts/generate_wan22_video_film.py input/my-image.jpg --frames 25
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional
import random
import subprocess
import shutil

# ComfyUI API settings
DEFAULT_COMFYUI_URL = "http://localhost:8188"
API_PROMPT_TEMPLATE_PATH = "user/default/workflows/video_wan2_2_14B_i2v_PNG_FILM.json"

def get_source_name(image_path: str) -> str:
    """Extract a clean source name from the image path."""
    filename = Path(image_path).stem
    clean_name = filename.replace("sogni-photobooth-", "").replace("-raw", "")
    clean_name = clean_name.replace(" ", "-").replace("_", "-")
    return clean_name

def calculate_duration(frames: int, fps: int = 16) -> str:
    """Calculate video duration and format as string."""
    duration = frames / fps
    return f"{duration:.1f}s"

def load_api_prompt_template() -> Dict[str, Any]:
    """Load the PNG workflow template."""
    with open(API_PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_api_prompt(
    workflow: Dict[str, Any],
    image_path: str,
    frames: int,
    width: int,
    height: int,
    source_name: str,
    settings: str = "4step_nosage"
) -> Dict[str, Any]:
    """Update workflow with image path and dynamic filename."""
    
    duration = calculate_duration(frames)
    
    # Build filename pattern for PNG sequence
    filename_pattern = f"frames/{source_name}_{width}x{height}_{frames}f_{duration}_{settings}_%year%%month%%day%_%hour%%minute%%second%"
    
    # Generate random seed for node 86
    seed = random.randint(0, 2**48)
    
    # Find nodes by ID in the nodes list
    nodes = workflow['nodes']
    
    # Update LoadImage node (ID 97)
    for node in nodes:
        if node['id'] == 97:
            node['widgets_values'] = [os.path.basename(image_path), "image"]
            break
    
    # Update WanImageToVideo node (ID 98)
    for node in nodes:
        if node['id'] == 98:
            node['widgets_values'] = [width, height, frames, 1]
            break
    
    # Update SaveImage node (ID 108)
    for node in nodes:
        if node['id'] == 108:
            node['widgets_values'] = [filename_pattern]
            break
    
    # Update KSampler seed (ID 86)
    for node in nodes:
        if node['id'] == 86:
            # Find the noise_seed widget (index 1 in widgets_values)
            if len(node['widgets_values']) > 1:
                node['widgets_values'][1] = seed
            break
    
    return workflow

def convert_workflow_to_api_format(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert ComfyUI frontend workflow format to API format.
    
    Frontend format: {"nodes": [{"id": 1, "type": "NodeType", ...}], ...}
    API format: {"1": {"class_type": "NodeType", "inputs": {...}, ...}, ...}
    """
    # Skip these node types (documentation nodes)
    skip_types = {'Note', 'MarkdownNote'}
    
    api_nodes = {}
    
    for node in workflow['nodes']:
        # Skip documentation nodes
        if node.get('type') in skip_types:
            continue
            
        node_id = str(node['id'])
        
        # Build inputs dict
        inputs = {}
        for inp in node.get('inputs', []):
            if 'link' in inp and inp['link'] is not None:
                # This is a connection to another node
                # Need to find which node output this connects to
                link_id = inp['link']
                # Find the link in the workflow
                for link in workflow['links']:
                    if link[0] == link_id:
                        # link format: [link_id, source_node_id, source_output_index, dest_node_id, dest_input_index]
                        source_node_id = str(link[1])
                        source_output_index = link[2]
                        inputs[inp['name']] = [source_node_id, source_output_index]
                        break
            elif 'widget' in inp:
                # This is a widget input, value comes from widgets_values
                pass
        
        # Add widget values to inputs
        if 'widgets_values' in node and node['widgets_values']:
            # Match widgets to their input names
            widget_idx = 0
            for inp in node.get('inputs', []):
                if 'widget' in inp:
                    if widget_idx < len(node['widgets_values']):
                        inputs[inp['name']] = node['widgets_values'][widget_idx]
                        widget_idx += 1
        
        api_nodes[node_id] = {
            'class_type': node['type'],
            'inputs': inputs
        }
    
    return api_nodes

def queue_prompt(prompt: Dict[str, Any], comfyui_url: str) -> Optional[str]:
    """Submit prompt to ComfyUI and return the prompt_id."""
    try:
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
    except urllib.error.URLError as e:
        print(f"[ERROR] Error connecting to ComfyUI: {e}")
        return None

def get_history(prompt_id: str, comfyui_url: str) -> Optional[Dict]:
    """Get the history for a prompt_id."""
    try:
        req = urllib.request.Request(f"{comfyui_url}/history/{prompt_id}")
        with urllib.request.urlopen(req) as response:
            history = json.loads(response.read())
            return history.get(prompt_id)
    except:
        return None

def wait_for_completion(prompt_id: str, comfyui_url: str, timeout: int = 600) -> bool:
    """Wait for workflow to complete."""
    start_time = time.time()
    print("\n[INFO] Waiting for generation to complete...")
    
    while True:
        if time.time() - start_time > timeout:
            print(f"[TIMEOUT] Timeout after {timeout}s")
            return False
        
        history = get_history(prompt_id, comfyui_url)
        if history:
            status = history.get("status", {})
            if status.get("completed", False):
                print("[SUCCESS] Generation completed!")
                return True
            elif "error" in status:
                print(f"[ERROR] Generation failed: {status['error']}")
                return False
        
        time.sleep(2)

def get_frames_directory(prompt_id: str, comfyui_url: str, source_name: str) -> Optional[str]:
    """Get the output frames directory from history."""
    history = get_history(prompt_id, comfyui_url)
    if history and "outputs" in history:
        for node_id, output in history["outputs"].items():
            if "images" in output:
                images = output["images"]
                if images and len(images) > 0:
                    subfolder = images[0].get("subfolder", "")
                    # The subfolder contains our frames
                    frames_dir = Path("output") / subfolder
                    if frames_dir.exists():
                        return str(frames_dir)
    
    # Fallback: search for matching directory
    frames_base = Path("output") / "frames"
    if frames_base.exists():
        # Find most recent directory matching source name
        matching_dirs = sorted(frames_base.glob(f"{source_name}*"), key=os.path.getmtime, reverse=True)
        if matching_dirs:
            return str(matching_dirs[0])
    
    return None

def run_film_interpolation(frames_dir: str, output_video: str, crf: int = 18) -> bool:
    """Run FILM interpolation on PNG frames."""
    print("\n" + "=" * 70)
    print("FILM Frame Interpolation (16fps -> 32fps)")
    print("=" * 70)
    print(f"[INFO] Frames directory: {frames_dir}")
    print(f"[INFO] Output video: {output_video}")
    print(f"[INFO] Quality: CRF {crf} (excellent)")
    
    # Run interpolation pipeline
    cmd = [
        sys.executable,
        "scripts/interpolate_pipeline.py",
        "--frames", frames_dir,
        "--fps", "16",
        "--method", "film",
        "--crf", str(crf),
        "--output", output_video
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FILM interpolation failed: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate Wan 2.2 i2v video with PNG + FILM interpolation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: 25 frames, 832x1216 portrait, auto FILM interpolation
  python scripts/generate_wan22_video_film.py input/my-image.jpg
  
  # Custom frame count (5 second video)
  python scripts/generate_wan22_video_film.py input/my-image.jpg --frames 81
  
  # Square video
  python scripts/generate_wan22_video_film.py input/my-image.jpg --width 1024 --height 1024 --frames 81
  
  # Maximum quality (CRF 10, near-lossless)
  python scripts/generate_wan22_video_film.py input/my-image.jpg --crf 10
        """
    )
    
    parser.add_argument("image_path", help="Path to the source image")
    parser.add_argument("--frames", type=int, default=25, help="Number of frames (default: 25)")
    parser.add_argument("--width", type=int, default=832, help="Video width (default: 832)")
    parser.add_argument("--height", type=int, default=1216, help="Video height (default: 1216)")
    parser.add_argument("--settings", default="4step_nosage", help="Settings tag (default: 4step_nosage)")
    parser.add_argument("--url", default=DEFAULT_COMFYUI_URL, help=f"ComfyUI URL (default: {DEFAULT_COMFYUI_URL})")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds (default: 600)")
    parser.add_argument("--crf", type=int, default=18, help="Output quality: 10=near-lossless, 18=excellent (default: 18)")
    parser.add_argument("--no-film", action="store_true", help="Skip FILM interpolation (PNG frames only)")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.image_path):
        print(f"[ERROR] Image not found: {args.image_path}")
        return 1
    
    if not os.path.exists(API_PROMPT_TEMPLATE_PATH):
        print(f"[ERROR] Workflow template not found: {API_PROMPT_TEMPLATE_PATH}")
        print("Run: python scripts/create_png_workflow.py")
        return 1
    
    # Get source name
    source_name = get_source_name(args.image_path)
    duration = calculate_duration(args.frames)
    
    # Print header
    print("=" * 70)
    print("Wan 2.2 i2v Video Generation + FILM Interpolation")
    print("=" * 70)
    print(f"Source Image:  {args.image_path}")
    print(f"Source Name:   {source_name}")
    print(f"Resolution:    {args.width}x{args.height}")
    print(f"Frames:        {args.frames} ({duration} @ 16fps)")
    print(f"Settings:      {args.settings}")
    print(f"Workflow:      {API_PROMPT_TEMPLATE_PATH}")
    print(f"ComfyUI URL:   {args.url}")
    print(f"FILM:          {'Enabled' if not args.no_film else 'Disabled'}")
    if not args.no_film:
        print(f"Output Quality: CRF {args.crf}")
    print("=" * 70)
    
    # Load and update workflow
    print("\n[INFO] Loading PNG workflow...")
    workflow = load_api_prompt_template()
    workflow = update_api_prompt(
        workflow,
        args.image_path,
        args.frames,
        args.width,
        args.height,
        source_name,
        args.settings
    )
    
    # Submit to ComfyUI
    print("[INFO] Submitting to ComfyUI...")
    
    # Convert workflow to API format
    print("[INFO] Converting workflow to API format...")
    api_prompt = convert_workflow_to_api_format(workflow)
    
    prompt_id = queue_prompt(api_prompt, args.url)
    
    if not prompt_id:
        print("[ERROR] Failed to queue prompt")
        return 1
    
    print(f"[SUCCESS] Prompt queued with ID: {prompt_id}")
    
    # Wait for completion
    success = wait_for_completion(prompt_id, args.url, args.timeout)
    
    if not success:
        print("\n[ERROR] Generation failed or timed out")
        return 1
    
    # Get frames directory
    frames_dir = get_frames_directory(prompt_id, args.url, source_name)
    
    if not frames_dir:
        print("\n[WARNING] Could not determine frames directory")
        print("   Check output/frames/ manually")
        return 1
    
    print(f"\n[SUCCESS] PNG frames saved: {frames_dir}")
    
    # Count frames
    frame_files = list(Path(frames_dir).glob("*.png"))
    print(f"[INFO] Frame count: {len(frame_files)}")
    
    # Run FILM interpolation
    if not args.no_film:
        # Generate output filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_video = f"output/video/{source_name}_{args.width}x{args.height}_{args.frames}f_{duration}_{args.settings}_{timestamp}_film_32fps_hq.mp4"
        
        success = run_film_interpolation(frames_dir, output_video, args.crf)
        
        if success:
            print("\n" + "=" * 70)
            print("Complete!")
            print("=" * 70)
            print(f"[SUCCESS] Final video: {output_video}")
            
            # Optionally cleanup frames
            response = input("\nDelete PNG frames? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(frames_dir)
                print(f"[INFO] Deleted frames: {frames_dir}")
            else:
                print(f"[INFO] Frames preserved: {frames_dir}")
            
            return 0
        else:
            print("\n[ERROR] FILM interpolation failed")
            print(f"[INFO] Frames available at: {frames_dir}")
            return 1
    else:
        print("\n[INFO] FILM interpolation skipped")
        print(f"[INFO] Process frames manually with:")
        print(f"  python scripts/interpolate_pipeline.py --frames {frames_dir} --fps 16 --method film --crf {args.crf}")
        return 0

if __name__ == "__main__":
    sys.exit(main())


