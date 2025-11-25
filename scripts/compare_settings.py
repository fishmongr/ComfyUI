import json

# Load workflows
with open('user/default/workflows/openart_wan22_extracted.json', 'r', encoding='utf-8') as f:
    openart = json.load(f)

with open('user/default/workflows/video_wan2_2_14B_i2v_no_sage_test.json', 'r', encoding='utf-8') as f:
    yours = json.load(f)

print("=" * 60)
print("SAMPLER SETTINGS COMPARISON")
print("=" * 60)

print("\nOPENART:")
samplers = [n for n in openart['nodes'] if 'Sampler' in n['type']]
for s in samplers:
    widgets = s['widgets_values']
    print(f"\n{s.get('title', s['type'])}:")
    print(f"  Steps: {widgets[0]}")
    print(f"  CFG: {widgets[1]}")  
    print(f"  Shift: {widgets[2]}")

print("\n\nYOUR WORKFLOW:")
samplers = [n for n in yours['nodes'] if 'KSampler' in n['type'] and n.get('mode', 0) == 0]
for s in samplers:
    widgets = s['widgets_values']
    print(f"\nNode {s['id']}:")
    print(f"  Steps: {widgets[3] if len(widgets) > 3 else 'N/A'}")
    print(f"  CFG: {widgets[4] if len(widgets) > 4 else 'N/A'}")
    if len(widgets) > 9:
        print(f"  Start step: {widgets[9]}")
        print(f"  End step: {widgets[10]}")

print("\n" + "=" * 60)
print("IMAGE/VIDEO SIZE COMPARISON")
print("=" * 60)

# Find WanImageToVideo or similar
openart_i2v = [n for n in openart['nodes'] if 'ImageToVideo' in n['type'] or 'EmptyEmbeds' in n['type']]
yours_i2v = [n for n in yours['nodes'] if 'ImageToVideo' in n['type'] and n.get('mode', 0) == 0]

print("\nOPENART:")
for n in openart_i2v[:1]:  # Just first one
    if 'widgets_values' in n:
        w = n['widgets_values']
        print(f"  Width x Height x Frames: {w[0] if len(w) > 0 else 'N/A'} x {w[1] if len(w) > 1 else 'N/A'} x {w[2] if len(w) > 2 else 'N/A'}")

print("\nYOUR WORKFLOW:")
for n in yours_i2v:
    w = n['widgets_values']
    print(f"  Width x Height x Frames: {w[0]} x {w[1]} x {w[2]}")

