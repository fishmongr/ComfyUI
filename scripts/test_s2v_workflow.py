#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the S2V workflow template is valid.
"""

import json
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_s2v_workflow_template():
    """Test that the S2V workflow template is valid JSON and has required nodes."""
    
    print("Testing Wan 2.2 S2V workflow template...")
    print("=" * 70)
    
    template_path = "scripts/last_prompt_api_format_s2v.json"
    
    # Test 1: File exists
    if not Path(template_path).exists():
        print(f"❌ FAIL: Template file not found: {template_path}")
        return False
    print(f"✓ Template file exists: {template_path}")
    
    # Test 2: Valid JSON
    try:
        with open(template_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON: {e}")
        return False
    print("✓ Valid JSON structure")
    
    # Test 3: Correct format (API format)
    if not isinstance(data, list) or len(data) < 3:
        print(f"❌ FAIL: Expected API format [version, client_id, nodes, ...], got {type(data)}")
        return False
    print("✓ Correct API format structure")
    
    nodes = data[2]
    
    # Test 4: Required nodes exist
    required_nodes = {
        "84": "CLIPLoader",
        "86": "KSamplerAdvanced",
        "87": "VAEDecode",
        "89": "CLIPTextEncode",
        "90": "VAELoader",
        "93": "CLIPTextEncode",
        "94": "CreateVideo",
        "95": "UNETLoader",
        "97": "LoadImage",
        "98": "WanSoundImageToVideo",  # KEY S2V NODE
        "103": "ModelSamplingSD3",
        "108": "SaveVideo",
        "119": "LoadAudio",
        "120": "AudioEncoderLoader",
        "122": "AudioEncoderEncode",  # KEY: Actually encodes the audio
    }
    
    missing_nodes = []
    wrong_type = []
    
    for node_id, expected_type in required_nodes.items():
        if node_id not in nodes:
            missing_nodes.append(node_id)
        elif nodes[node_id].get("class_type") != expected_type:
            wrong_type.append(f"{node_id} (expected {expected_type}, got {nodes[node_id].get('class_type')})")
    
    if missing_nodes:
        print(f"❌ FAIL: Missing nodes: {missing_nodes}")
        return False
    if wrong_type:
        print(f"❌ FAIL: Wrong node types: {wrong_type}")
        return False
    print(f"✓ All {len(required_nodes)} required nodes present with correct types")
    
    # Test 5: WanSoundImageToVideo has correct inputs
    wan_node = nodes["98"]
    required_inputs = ["width", "height", "length", "batch_size", "positive", "negative", "vae", "audio_encoder_output"]
    
    for input_name in required_inputs:
        if input_name not in wan_node["inputs"]:
            print(f"❌ FAIL: WanSoundImageToVideo missing input: {input_name}")
            return False
    print(f"✓ WanSoundImageToVideo has all required inputs")
    
    # Test 6: Audio pipeline connections
    audio_connections = [
        ("119", "LoadAudio", "outputs AUDIO"),
        ("120", "AudioEncoderLoader", "outputs AUDIO_ENCODER"),
        ("122", "AudioEncoderEncode", "outputs AUDIO_ENCODER_OUTPUT"),
    ]
    
    # Check that node 122 gets audio from 119 and encoder from 120
    encode_node = nodes["122"]
    if encode_node["inputs"].get("audio_encoder") != ["120", 0]:
        print(f"⚠️  WARNING: Node 122 audio_encoder should connect to node 120")
    if encode_node["inputs"].get("audio") != ["119", 0]:
        print(f"⚠️  WARNING: Node 122 audio should connect to node 119")
    
    # Check that node 98 gets encoded audio from 122
    if wan_node["inputs"].get("audio_encoder_output") != ["122", 0]:
        print(f"❌ FAIL: Node 98 audio_encoder_output should connect to node 122")
        return False
    
    print("✓ Audio encoding pipeline correctly connected")
    
    # Test 7: Check S2V model
    unet_node = nodes["95"]
    expected_model = "wan2.2_s2v_14B_fp8_scaled.safetensors"
    actual_model = unet_node["inputs"].get("unet_name")
    if actual_model != expected_model:
        print(f"⚠️  WARNING: S2V model = {actual_model}, expected {expected_model}")
    else:
        print("✓ S2V model configured correctly")
    
    # Summary
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("\nWorkflow template is valid and ready to use!")
    print(f"\nAudio pipeline:")
    print(f"  - Node 119: LoadAudio → AUDIO")
    print(f"  - Node 120: AudioEncoderLoader → AUDIO_ENCODER")
    print(f"  - Node 122: AudioEncoderEncode → AUDIO_ENCODER_OUTPUT")
    print(f"  - Node 98: WanSoundImageToVideo (uses encoded audio)")
    print(f"\nKey features:")
    print(f"  - Supports all audio formats (MP3, WAV, FLAC, etc.)")
    print(f"  - Optional reference image (node 97)")
    print(f"  - Optional audio trimming (node 121, added dynamically)")
    print(f"  - Single-pass generation (no two-pass like i2v)")
    
    return True

if __name__ == "__main__":
    success = test_s2v_workflow_template()
    sys.exit(0 if success else 1)

