#!/usr/bin/env python3
"""
Test the PNG+FILM workflow by queueing it to ComfyUI
"""

import json
import sys
import urllib.request
import urllib.error

sys.path.insert(0, 'scripts')
from generate_wan22_video_film import load_api_prompt_template, update_api_prompt, convert_workflow_to_api_format

# Load and update workflow
print("[TEST] Loading workflow...")
workflow = load_api_prompt_template()

print(f"[TEST] Workflow has {len(workflow['nodes'])} nodes")
print(f"[TEST] Sample node structure:")
sample_node = workflow['nodes'][0]
print(f"  Node ID: {sample_node['id']}, Type: {sample_node.get('type')}")

# Update with test data
print("\n[TEST] Updating workflow with test image...")
workflow = update_api_prompt(
    workflow,
    'input/download-10.jpg',
    25,
    832,
    1216,
    'test-image',
    '4step_nosage'
)

# Try to queue it
print("\n[TEST] Converting workflow to API format...")
api_prompt = convert_workflow_to_api_format(workflow)
print(f"[TEST] API format has {len(api_prompt)} nodes")
print(f"[TEST] Sample API node:")
sample_api_node_id = list(api_prompt.keys())[0]
print(f"  Node ID: {sample_api_node_id}, class_type: {api_prompt[sample_api_node_id].get('class_type')}")

print("\n[TEST] Attempting to queue workflow to ComfyUI...")
comfyui_url = "http://localhost:8188"

try:
    data = json.dumps({"prompt": api_prompt}).encode('utf-8')
    req = urllib.request.Request(
        f"{comfyui_url}/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        prompt_id = result.get("prompt_id")
        
        if prompt_id:
            print(f"[SUCCESS] Workflow queued successfully!")
            print(f"Prompt ID: {prompt_id}")
            sys.exit(0)
        else:
            print(f"[ERROR] No prompt_id in response: {result}")
            sys.exit(1)
            
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"[ERROR] HTTP Error {e.code}:")
    print(error_body)
    
    # Try to parse error
    try:
        error_json = json.loads(error_body)
        print(f"\nError details: {json.dumps(error_json, indent=2)}")
    except:
        pass
    
    sys.exit(1)
    
except urllib.error.URLError as e:
    print(f"[ERROR] Could not connect to ComfyUI at {comfyui_url}")
    print(f"Make sure ComfyUI is running!")
    print(f"Error: {e}")
    sys.exit(1)

