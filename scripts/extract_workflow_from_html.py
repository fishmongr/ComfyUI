"""
Extract workflow JSON from OpenArt HTML page
"""
import sys
import re
import json

if len(sys.argv) < 2:
    print("Usage: python extract_workflow_from_html.py <html_file>")
    sys.exit(1)

html_file = sys.argv[1]

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Try multiple patterns to find workflow JSON
patterns = [
    r'"workflow"\s*:\s*(\{.*?\})\s*,',
    r'"workflowData"\s*:\s*(\{.*?\})\s*,',
    r'workflowJson\s*:\s*(\{.*?\})',
    r'__NEXT_DATA__.*?type.*?application/json.*?>(.*?)</script>',
]

for pattern in patterns:
    match = re.search(pattern, content, re.DOTALL)
    if match:
        try:
            workflow_json = json.loads(match.group(1))
            output_file = html_file.replace('.html', '_workflow.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_json, f, indent=2)
            print(f"Extracted workflow to: {output_file}")
            sys.exit(0)
        except json.JSONDecodeError:
            continue

print("Could not extract workflow JSON from HTML")
print("The page might require JavaScript to load the workflow data")
print("\nPlease manually download the workflow JSON from the OpenArt page:")
print("1. Visit: https://openart.ai/workflows/dowhatyouwantcuzapirateisfree/wan-22-t2v-for-high-end-systems-speed-and-quality-focused/97QzdiAgLDihbeoSKHIt")
print("2. Click the 'Download' or 'Export' button")
print("3. Save as: user/default/workflows/openart_wan22_reference.json")
sys.exit(1)

