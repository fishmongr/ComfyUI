"""
Find Maximum Frame Count Without RAM Offloading
Tests incrementally to find the sweet spot where model stays fully in VRAM.
"""

import requests
import json
import time
import sys
import os

def test_frame_count(frames, comfyui_url="http://localhost:8188"):
    """Test a specific frame count and check for RAM offloading."""
    
    workflow_path = "user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json"
    
    print(f"\n{'='*70}")
    print(f"Testing {frames} frames ({frames/16:.2f}s @ 16fps)")
    print(f"{'='*70}")
    
    # Load workflow
    with open(workflow_path, 'r') as f:
        workflow_data = json.load(f)
    
    # Update frame count
    for node_id, node_data in workflow_data.items():
        if node_data.get('class_type') == 'WanImageToVideo':
            if 'inputs' in node_data:
                node_data['inputs']['length'] = frames
    
    # Submit to ComfyUI
    try:
        response = requests.post(f"{comfyui_url}/prompt", json={"prompt": workflow_data})
        response.raise_for_status()
        prompt_id = response.json()['prompt_id']
        print(f"✓ Prompt queued: {prompt_id}")
    except Exception as e:
        print(f"❌ Failed to submit: {e}")
        return None
    
    # Monitor execution
    start_time = time.time()
    last_status = ""
    offload_detected = False
    execution_time = None
    
    while True:
        time.sleep(2)
        
        try:
            # Check history
            history_response = requests.get(f"{comfyui_url}/history/{prompt_id}")
            if history_response.status_code == 200:
                history = history_response.json()
                
                if prompt_id in history:
                    status_data = history[prompt_id].get('status', {})
                    status = status_data.get('status_str', 'unknown')
                    
                    if status != last_status:
                        print(f"Status: {status}")
                        last_status = status
                    
                    if status == 'success':
                        execution_time = time.time() - start_time
                        print(f"✅ Completed in {execution_time:.1f}s")
                        break
                    elif status == 'error':
                        print(f"❌ Error occurred")
                        return None
            
            # Check system stats for offloading
            stats_response = requests.get(f"{comfyui_url}/system_stats")
            if stats_response.status_code == 200:
                # We can't directly check from stats, but we can infer from execution time
                pass
                
        except Exception as e:
            # Connection issues, likely still processing
            pass
        
        # Timeout after 10 minutes
        if time.time() - start_time > 600:
            print(f"⏱️ Timeout after 10 minutes")
            return None
    
    return {
        'frames': frames,
        'duration': frames / 16,
        'execution_time': execution_time,
        'time_per_frame': execution_time / frames if execution_time else None
    }


def binary_search_max_frames(min_frames=81, max_frames=161, target_time_per_frame=2.0):
    """
    Binary search to find maximum frames before RAM offloading kicks in.
    
    Strategy:
    - 81 frames = 1.89s/frame (153.54s / 81) ✅ Full VRAM
    - 161 frames = 3.06s/frame (493.30s / 161) ❌ RAM offload (4x slower)
    - Target: Find frame count where time/frame < 2.0s (some margin)
    """
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  Finding Maximum Frame Count for Full VRAM Loading                  ║
╚══════════════════════════════════════════════════════════════════════╝

Known benchmarks:
  • 81 frames:  153.54s = 1.89s/frame ✅ (Full VRAM)
  • 161 frames: 493.30s = 3.06s/frame ❌ (RAM offload)

Target: < {target_time_per_frame}s/frame (indicates full VRAM loading)

Testing strategy: Binary search between {min_frames} and {max_frames} frames
""")
    
    input("Press Enter to start testing (make sure ComfyUI is running)...")
    
    results = []
    
    # Test bounds first
    test_points = [
        97,   # 6s
        113,  # 7s  
        129,  # 8s
        145,  # 9s
    ]
    
    for frames in test_points:
        result = test_frame_count(frames)
        if result:
            results.append(result)
            
            time_per_frame = result['time_per_frame']
            if time_per_frame > target_time_per_frame:
                print(f"\n⚠️ RAM offload detected at {frames} frames ({time_per_frame:.2f}s/frame)")
                break
            else:
                print(f"\n✅ Full VRAM at {frames} frames ({time_per_frame:.2f}s/frame)")
        
        # Wait between tests
        print("\nWaiting 10s before next test...")
        time.sleep(10)
    
    # Print summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Frames':<8} {'Duration':<10} {'Time (s)':<10} {'s/frame':<10} {'Status':<15}")
    print(f"{'-'*70}")
    
    for r in results:
        status = "✅ Full VRAM" if r['time_per_frame'] < target_time_per_frame else "❌ RAM offload"
        print(f"{r['frames']:<8} {r['duration']:.2f}s{'':<5} {r['execution_time']:<10.1f} {r['time_per_frame']:<10.2f} {status}")
    
    # Find maximum safe frames
    safe_results = [r for r in results if r['time_per_frame'] < target_time_per_frame]
    if safe_results:
        max_safe = max(safe_results, key=lambda x: x['frames'])
        print(f"\n🎯 Maximum safe frame count: {max_safe['frames']} frames ({max_safe['duration']:.2f}s)")
        print(f"   Expected time: ~{max_safe['execution_time']:.1f}s per video")
    
    # Save results
    output_file = "docs/max_frames_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Results saved to: {output_file}")


if __name__ == "__main__":
    binary_search_max_frames()


