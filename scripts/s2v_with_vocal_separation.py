#!/usr/bin/env python3
"""
S2V with Automatic Vocal Separation

Automatically separates vocals from audio using Demucs,
then generates S2V video with the isolated vocals for better lip sync.

Usage:
    python s2v_with_vocal_separation.py audio_file [S2V_OPTIONS]

Example:
    python s2v_with_vocal_separation.py "input/song.mp3" \
        --ref-image input/face.jpg \
        --frames 97 \
        --positive "woman singing passionately" \
        --interpolate film
"""

import subprocess
import sys
from pathlib import Path
import argparse

def separate_vocals_demucs(audio_path, output_dir="input/vocals", model="htdemucs_ft"):
    """Separate vocals using Demucs (best quality)."""
    print(f"\n{'='*70}")
    print(f"Separating vocals with Demucs ({model})...")
    print(f"{'='*70}")
    print(f"Input: {audio_path}")
    
    cmd = [
        "demucs",
        "-n", model,
        "--two-stems", "vocals",
        "-o", output_dir,
        str(audio_path)
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error during vocal separation:")
        print(result.stderr)
        sys.exit(1)
    
    # Find output vocal file
    audio_name = Path(audio_path).stem
    
    # Try different path structures
    possible_paths = [
        Path(output_dir) / model / audio_name / "vocals.wav",
        Path(output_dir) / "htdemucs_ft" / audio_name / "vocals.wav",
        Path(output_dir) / "htdemucs" / audio_name / "vocals.wav",
    ]
    
    vocal_file = None
    for path in possible_paths:
        if path.exists():
            vocal_file = path
            break
    
    if not vocal_file:
        print(f"\nError: Could not find vocal output")
        print(f"Expected locations:")
        for path in possible_paths:
            print(f"  - {path}")
        sys.exit(1)
    
    file_size = vocal_file.stat().st_size / (1024 * 1024)  # MB
    print(f"\n✓ Vocals extracted: {vocal_file}")
    print(f"  File size: {file_size:.2f} MB")
    print(f"\n  You can listen to the isolated vocals at:")
    print(f"  {vocal_file.absolute()}")
    
    return vocal_file

def main():
    parser = argparse.ArgumentParser(
        description="Generate S2V video with automatic vocal separation",
        epilog="""
Examples:
  # Basic usage
  python s2v_with_vocal_separation.py input/song.mp3 --ref-image input/face.jpg

  # With all options
  python s2v_with_vocal_separation.py input/song.mp3 \\
      --ref-image input/face.jpg \\
      --frames 97 \\
      --positive "woman singing passionately" \\
      --interpolate film

  # Use faster separation model
  python s2v_with_vocal_separation.py input/song.mp3 \\
      --separation-model htdemucs \\
      --ref-image input/face.jpg
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("audio_file", help="Input audio file (any format)")
    parser.add_argument("--separation-model", 
                       choices=["htdemucs", "htdemucs_ft", "htdemucs_6s"],
                       default="htdemucs_ft",
                       help="Demucs model (default: htdemucs_ft - best balance)")
    parser.add_argument("--skip-separation", 
                       action="store_true",
                       help="Skip vocal separation (use if already separated)")
    
    # Parse known args, pass rest to S2V script
    args, s2v_args = parser.parse_known_args()
    
    audio_file = Path(args.audio_file)
    if not audio_file.exists():
        print(f"Error: Audio file not found: {audio_file}")
        sys.exit(1)
    
    # Step 1: Separate vocals (unless skipped)
    if args.skip_separation:
        print(f"Skipping vocal separation, using original audio...")
        vocal_file = audio_file
    else:
        vocal_file = separate_vocals_demucs(
            audio_file,
            model=args.separation_model
        )
    
    # Step 2: Generate S2V with vocals
    s2v_cmd = [
        sys.executable,
        "scripts/generate_wan22_sound_video.py",
        str(vocal_file)
    ] + s2v_args
    
    print(f"\n{'='*70}")
    print("Generating S2V video with isolated vocals...")
    print(f"{'='*70}\n")
    print(f"Command: {' '.join(s2v_cmd)}\n")
    
    result = subprocess.run(s2v_cmd)
    
    # Remind user where the vocals are saved
    if not args.skip_separation:
        print(f"\n{'='*70}")
        print("VOCAL FILES SAVED")
        print(f"{'='*70}")
        print(f"Isolated vocals: {vocal_file.absolute()}")
        print(f"No vocals (instrumental): {vocal_file.parent / 'no_vocals.wav'}")
        print(f"\nYou can listen to these files anytime!")
        print(f"{'='*70}\n")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()

