#!/usr/bin/env python3
"""
Export ComfyUI workflow from frontend format to API format.
Load a workflow in ComfyUI and use "Save (API Format)" option.
This script helps automate the conversion if needed.
"""

import json
import sys

def main():
    print("\n⚠️  WORKFLOW FORMAT ISSUE")
    print("="*70)
    print("The workflow file is in FRONTEND format, but the API needs")
    print("the API format.")
    print()
    print("To fix this:")
    print("  1. Open ComfyUI in your browser: http://127.0.0.1:8188")
    print("  2. Load your workflow")
    print("  3. Click the gear icon (⚙️) → 'Save (API Format)'")
    print("  4. Save as: workflows/video_wan2_2_14B_i2v_api.json")
    print("  5. Use --workflow workflows/video_wan2_2_14B_i2v_api.json")
    print("="*70)
    print()

if __name__ == "__main__":
    main()


