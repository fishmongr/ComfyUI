# TaylorSeer Node Not Loaded - Verification Script

import urllib.request
import json

# Check if TaylorSeer is loaded by querying ComfyUI's object_info
url = "http://127.0.0.1:8188/object_info"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))

# Check if TaylorSeerLite exists
if "TaylorSeerLite" in data:
    print("[SUCCESS] TaylorSeerLite IS loaded!")
    print(f"Node info: {json.dumps(data['TaylorSeerLite'], indent=2)}")
else:
    print("[FAIL] TaylorSeerLite is NOT loaded!")
    print("\nAvailable Taylor/Seer nodes:")
    for node_name in sorted(data.keys()):
        if "taylor" in node_name.lower() or "seer" in node_name.lower():
            print(f"  - {node_name}")
    
    if not any("taylor" in n.lower() or "seer" in n.lower() for n in data.keys()):
        print("  (None found)")
    
    print("\n[ALERT] TaylorSeer custom node failed to load!")
    print("\nCheck ComfyUI startup logs for errors like:")
    print('  - "Cannot load module..."')
    print('  - "Import error..."')
    print('  - "ModuleNotFoundError..."')

