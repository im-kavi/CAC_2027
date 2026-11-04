#!/usr/bin/env python3
"""
Test script for running best.pt segmentation directly on ZED 2i camera.
Directly binds to the active video capture stream and runs real-time YOLOv8 segmentation.
"""

import os
import time
import cv2
import numpy as np
from ultralytics import YOLO

MODEL_PATH = "/home/kavi/CAC_27/kavi_ws/src/local_obstacle_avoidance/models/best.pt"
CONF_THRESHOLD = 0.35


def get_working_zed_capture():
    """Find and return an opened VideoCapture for the ZED camera."""
    # Test indices, prioritizing index 2 which is the ZED 2i
    for idx in [2, 0, 4, 6]:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                # ZED transmits side-by-side frames (width ~ 2x to 3.5x height)
                if w >= h * 2:
                    print(f"      Connected to ZED 2i on /dev/video{idx} (resolution: {w}x{h})")
                    return cap
            cap.release()

    # Fallback to direct /dev/video2
    cap = cv2.VideoCapture(2)
    if cap.isOpened():
        return cap
    return None


def main():
    print("=" * 60)
    print("  ZED 2i + YOLOv8 (best.pt) Live Obstacle Detection Test")
    print("=" * 60)

    # 1. Load YOLO model
    print(f"[1/3] Loading YOLO model: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found at {MODEL_PATH}")
        return

    model = YOLO(MODEL_PATH)
    print(f"      Classes: {model.names}")

    # 2. Open Camera
    print("[2/3] Opening ZED 2i camera...")
    cap = get_working_zed_capture()

    if cap is None or not cap.isOpened():
        print("[ERROR] Could not open ZED camera stream.")
        print("        Ensure the camera is connected via USB.")
        return

    print("[3/3] Starting live inference window...")
    print("      -> Press 'q' or ESC in the window to exit.")
    print("=" * 60)

    window_name = "ZED 2i - Crater & Rock Detection (best.pt)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1000, 600)

    fps_count = 0
    fps_start = time.time()
    fps_val = 0.0

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        # Extract left eye from side-by-side stereo stream
        fh, fw = frame.shape[:2]
        if fw > fh * 2:
            left_frame = frame[:, :fw // 2]
        else:
            left_frame = frame

        # Run inference
        results = model.predict(
            source=left_frame,
            conf=CONF_THRESHOLD,
            retina_masks=True,
            verbose=False
        )

        res = results[0]
        annotated = res.plot()

        # Calculate FPS
        fps_count += 1
        elapsed = time.time() - fps_start
        if elapsed >= 1.0:
            fps_val = fps_count / elapsed
            fps_count = 0
            fps_start = time.time()

        # Display info overlay
        cv2.putText(
            annotated,
            f"FPS: {fps_val:.1f} | Detections: {len(res.boxes)}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow(window_name, annotated)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            print("\n[INFO] Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
