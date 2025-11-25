# Quick FlashAttention Test Script
# Tests PyTorch SDPA vs baseline on a short 25-frame generation

import subprocess
import time
import sys

def test_flashattention():
    """Test FlashAttention performance"""
    
    print("=" * 60)
    print("FlashAttention Quick Test - RTX 5090")
    print("=" * 60)
    print()
    
    # Test parameters
    image_path = "input/sogni-photobooth-my-polar-bear-baby-raw.jpg"
    frames = 25
    settings = "4step_flash_test"
    
    print(f"Test Configuration:")
    print(f"  Image: {image_path}")
    print(f"  Frames: {frames} (1.6s @ 16fps)")
    print(f"  Settings: {settings}")
    print(f"  Attention: PyTorch SDPA (FlashAttention backend)")
    print()
    
    # Check if image exists
    import os
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        print("Please ensure the test image exists before running.")
        return False
    
    print("Starting test generation...")
    print("This will:")
    print("  1. Launch ComfyUI with --use-pytorch-cross-attention")
    print("  2. Generate 25-frame video")
    print("  3. Report timing and VRAM usage")
    print()
    print("Press Ctrl+C to cancel...")
    print()
    
    try:
        time.sleep(2)
        
        # Run generation
        cmd = [
            sys.executable,
            "scripts/generate_wan22_video.py",
            image_path,
            "--frames", str(frames),
            "--settings", settings
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print()
        
        start_time = time.time()
        result = subprocess.run(cmd, check=True)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("TEST COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"Total time: {elapsed:.1f}s")
            print()
            print("Next steps:")
            print("  1. Check ComfyUI logs for 'Using pytorch attention'")
            print("  2. Compare timing against baseline (~75s for 81 frames)")
            print("  3. Run full benchmark suite if results look good")
            print()
            return True
        else:
            print("TEST FAILED")
            return False
            
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_flashattention()
    sys.exit(0 if success else 1)

