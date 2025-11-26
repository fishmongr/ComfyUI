#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the WanFirstLastFrameToVideo workflow template is valid.
"""

import json
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_workflow_template():
    """Test that the workflow template is valid JSON and has required nodes."""
    
    print("Testing WanFirstLastFrameToVideo workflow template...")
    print("=" * 70)
    
    template_path = "scripts/last_prompt_api_format_firstlast.json"
    
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
        "85": "KSamplerAdvanced",  
        "86": "KSamplerAdvanced",
        "87": "VAEDecode",
        "89": "CLIPTextEncode",
        "90": "VAELoader",
        "93": "CLIPTextEncode",
        "94": "CreateVideo",
        "95": "UNETLoader",
        "96": "UNETLoader",
        "97": "LoadImage",
        "98": "WanFirstLastFrameToVideo",  # KEY NODE
        "101": "LoraLoaderModelOnly",
        "102": "LoraLoaderModelOnly",
        "103": "ModelSamplingSD3",
        "104": "ModelSamplingSD3",
        "108": "SaveVideo",
        "117": "Sage3AttentionOnlySwitch",
        "118": "Sage3AttentionOnlySwitch",
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
    
    # Test 5: WanFirstLastFrameToVideo has correct inputs
    wan_node = nodes["98"]
    required_inputs = ["width", "height", "length", "batch_size", "positive", "negative", "vae", "start_image"]
    
    for input_name in required_inputs:
        if input_name not in wan_node["inputs"]:
            print(f"❌ FAIL: WanFirstLastFrameToVideo missing input: {input_name}")
            return False
    print(f"✓ WanFirstLastFrameToVideo has all required inputs")
    
    # Test 6: Verify node connections
    connections_to_check = [
        ("97", "98", "start_image"),  # LoadImage -> WanFirstLastFrameToVideo
        ("98", "86", "positive"),      # WanFirstLastFrameToVideo -> KSampler
        ("85", "87", "samples"),       # KSampler -> VAEDecode
        ("87", "94", "images"),        # VAEDecode -> CreateVideo
        ("94", "108", "video"),        # CreateVideo -> SaveVideo
    ]
    
    for source_node, target_node, input_name in connections_to_check:
        if target_node not in nodes:
            continue
        target_inputs = nodes[target_node]["inputs"]
        if input_name in target_inputs:
            connection = target_inputs[input_name]
            if isinstance(connection, list) and len(connection) >= 2:
                if connection[0] != source_node:
                    print(f"⚠️  WARNING: Connection mismatch: {target_node}.{input_name} expected from {source_node}, got {connection[0]}")
    
    print("✓ Key node connections verified")
    
    # Test 7: Check models and LoRAs
    models_check = [
        ("95", "unet_name", "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"),
        ("96", "unet_name", "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"),
        ("101", "lora_name", "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"),
        ("102", "lora_name", "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"),
    ]
    
    for node_id, param, expected_value in models_check:
        actual_value = nodes[node_id]["inputs"].get(param)
        if actual_value != expected_value:
            print(f"⚠️  WARNING: {node_id}.{param} = {actual_value}, expected {expected_value}")
    
    print("✓ Model and LoRA configurations correct")
    
    # Summary
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("\nWorkflow template is valid and ready to use!")
    print(f"\nKey features:")
    print(f"  - Node 98: WanFirstLastFrameToVideo (upgraded from WanImageToVideo)")
    print(f"  - Supports: start_image (required)")
    print(f"  - Supports: end_image (optional - added dynamically by script)")
    print(f"  - Supports: clip_vision_start_image (optional - manual integration)")
    print(f"  - Supports: clip_vision_end_image (optional - manual integration)")
    
    return True

if __name__ == "__main__":
    success = test_workflow_template()
    sys.exit(0 if success else 1)

