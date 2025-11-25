#!/usr/bin/env python3
"""
Auto Frame Interpolation Hook for ComfyUI Workflows
Automatically interpolates videos after workflow completion

This script can be integrated into the workflow generation script
to automatically process videos after they are generated.

Usage:
    # As a post-processing hook in generate_wan22_video.py
    from auto_interpolate_workflow import auto_interpolate

    # After video generation
    output_path = get_output_path(prompt_id, args.url)
    if output_path and args.auto_interpolate:
        auto_interpolate(output_path, method='rife')

    # Or run standalone
    python scripts/auto_interpolate_workflow.py --watch output/video/ --method rife

Author: ComfyUI Frame Interpolation
Date: 2025-11-24
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add ComfyUI to path
COMFYUI_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(COMFYUI_ROOT))

# Import interpolation functionality
try:
    from interpolate_video import VideoInterpolator, get_output_filename
except ImportError:
    print("[ERROR] Could not import interpolate_video module")
    print("Make sure interpolate_video.py is in the same directory")
    sys.exit(1)


def auto_interpolate(
    video_path: str,
    method: str = "rife",
    enable: bool = True,
    wait_time: float = 2.0
) -> Optional[str]:
    """
    Automatically interpolate a video after it's been generated

    Args:
        video_path: Path to the generated video
        method: Interpolation method ('rife', 'film', or 'both')
        enable: Whether interpolation is enabled
        wait_time: Seconds to wait before processing (to ensure file is complete)

    Returns:
        Path to interpolated video, or None if disabled/failed
    """
    if not enable:
        print("[INFO] Auto-interpolation is disabled")
        return None

    # Wait for file to be fully written
    if wait_time > 0:
        print(f"[INFO] Waiting {wait_time}s for video file to complete...")
        time.sleep(wait_time)

    # Check if video already interpolated
    if "_rife_32fps" in video_path or "_film_32fps" in video_path:
        print("[SKIP] Video already interpolated")
        return None

    print(f"\n{'='*70}")
    print(f"Auto Frame Interpolation - {method.upper()}")
    print(f"{'='*70}")
    print(f"Input: {video_path}")

    methods = ["rife", "film"] if method == "both" else [method]
    output_paths = []

    for m in methods:
        try:
            output_path = get_output_filename(video_path, m)
            print(f"\n[INFO] Processing with {m.upper()}...")

            interpolator = VideoInterpolator(method=m)
            success = interpolator.process_video(video_path, output_path, target_fps=32)

            if success:
                output_paths.append(output_path)
                print(f"[SUCCESS] {m.upper()} interpolation complete: {output_path}")
            else:
                print(f"[ERROR] {m.upper()} interpolation failed")

        except Exception as e:
            print(f"[ERROR] Failed to interpolate with {m}: {e}")

    if output_paths:
        return output_paths[0] if len(output_paths) == 1 else output_paths
    return None


class VideoFileHandler(FileSystemEventHandler):
    """Watches for new video files and auto-interpolates them"""

    def __init__(self, method: str = "rife", wait_time: float = 5.0):
        self.method = method
        self.wait_time = wait_time
        self.processing = set()
        super().__init__()

    def on_created(self, event):
        if event.is_directory:
            return

        # Only process .mp4 files
        if not event.src_path.endswith('.mp4'):
            return

        # Skip already interpolated videos
        if "_rife_32fps" in event.src_path or "_film_32fps" in event.src_path:
            return

        # Skip if already processing
        if event.src_path in self.processing:
            return

        print(f"\n[DETECTED] New video: {event.src_path}")

        # Mark as processing
        self.processing.add(event.src_path)

        try:
            # Auto-interpolate
            auto_interpolate(event.src_path, method=self.method, wait_time=self.wait_time)
        finally:
            # Remove from processing set
            self.processing.discard(event.src_path)

    def on_modified(self, event):
        # Sometimes file creation triggers modified event
        # Ignore it if we already have the file
        pass


def watch_directory(watch_path: str, method: str = "rife", wait_time: float = 5.0):
    """
    Watch a directory for new videos and auto-interpolate them

    Args:
        watch_path: Directory to watch
        method: Interpolation method
        wait_time: Seconds to wait after file creation before processing
    """
    watch_path = Path(watch_path)

    if not watch_path.exists():
        print(f"[ERROR] Watch directory does not exist: {watch_path}")
        return

    print(f"{'='*70}")
    print(f"ComfyUI Auto Frame Interpolation - Watching Mode")
    print(f"{'='*70}")
    print(f"Directory: {watch_path}")
    print(f"Method: {method.upper()}")
    print(f"Wait time: {wait_time}s")
    print(f"\n[INFO] Watching for new videos... (Press Ctrl+C to stop)")

    event_handler = VideoFileHandler(method=method, wait_time=wait_time)
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping watcher...")
        observer.stop()

    observer.join()
    print("[INFO] Watcher stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Auto Frame Interpolation for ComfyUI Workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch directory for new videos and auto-interpolate with RIFE
  python scripts/auto_interpolate_workflow.py --watch output/video/ --method rife

  # Watch and process with both RIFE and FILM for comparison
  python scripts/auto_interpolate_workflow.py --watch output/video/ --method both

  # Process a single video immediately
  python scripts/auto_interpolate_workflow.py --input output/video/polar-bear_*.mp4 --method rife
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--watch",
        help="Directory to watch for new videos"
    )

    group.add_argument(
        "--input",
        help="Single video file to process immediately"
    )

    parser.add_argument(
        "--method",
        choices=["rife", "film", "both"],
        default="rife",
        help="Interpolation method (default: rife)"
    )

    parser.add_argument(
        "--wait",
        type=float,
        default=5.0,
        help="Seconds to wait after file creation before processing (default: 5.0)"
    )

    args = parser.parse_args()

    if args.watch:
        # Watch mode
        watch_directory(args.watch, method=args.method, wait_time=args.wait)
    elif args.input:
        # Single file mode
        result = auto_interpolate(args.input, method=args.method, enable=True, wait_time=0)
        if result:
            print(f"\n[SUCCESS] Interpolation complete!")
            return 0
        else:
            print(f"\n[ERROR] Interpolation failed")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())




