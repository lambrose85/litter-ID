# litter_monitor.py
import cv2 as cv
import numpy as np
import yaml  # ← Add this import
import time
from datetime import datetime

# Import your logging module
import log

def load_config():
    """Simple config loader"""
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    # ========== LOAD CONFIGURATION ==========
    print("Loading configuration...")
    config = load_config()
    
    # ========== EXTRACT SETTINGS ==========
    # Camera settings
    camera_id = config["camera"]["device_id"]
    show_preview = config["camera"]["show_preview"]
    
    # Detection settings
    history = config["detection"]["history"]
    dist_threshold = config["detection"]["dist_threshold"]
    detect_shadows = config["detection"]["detect_shadows"]
    min_contour_area = config["detection"]["min_contour_area"]
    kernel_size = config["detection"]["kernel_size"]
    dilation_iterations = config["detection"]["dilation_iterations"]
    
    # Litter box settings
    x1_percent = config["litter_box"]["x1_percent"]
    y1_percent = config["litter_box"]["y1_percent"]
    x2_percent = config["litter_box"]["x2_percent"]
    y2_percent = config["litter_box"]["y2_percent"]
    min_usage_time = config["litter_box"]["min_usage_time"]
    
    # ========== INITIALIZE CAMERA ==========
    cam = cv.VideoCapture(camera_id)
    
    # Get actual frame dimensions
    frame_width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate litter box coordinates in pixels
    litter_box_coords = (
        int(frame_width * x1_percent),   # x1
        int(frame_height * y1_percent),  # y1
        int(frame_width * x2_percent),   # x2
        int(frame_height * y2_percent)   # y2
    )
    
    print(f"Camera: {frame_width}x{frame_height}")
    print(f"Litter box zone: {litter_box_coords}")
    
    # ========== INITIALIZE DETECTOR ==========
    bg_subtractor = cv.createBackgroundSubtractorKNN(
        history=history,
        dist2Threshold=dist_threshold,
        detectShadows=detect_shadows
    )
    
    # Create kernel for morphological operations
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # ========== MAIN LOOP ==========
    print("Starting monitoring... Press 'q' to quit")
    
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        
        # ========== MOTION DETECTION ==========
        fg_mask = bg_subtractor.apply(frame)
        
        # Noise reduction
        fg_mask = cv.morphologyEx(fg_mask, cv.MORPH_OPEN, kernel)
        fg_mask = cv.dilate(fg_mask, kernel, iterations=dilation_iterations)
        
        # Find contours
        contours, _ = cv.findContours(fg_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        # ========== CHECK LITTER BOX ZONE ==========
        motion_in_box = False
        
        for contour in contours:
            if cv.contourArea(contour) > min_contour_area:
                x, y, w, h = cv.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Check if center is in litter box
                if (litter_box_coords[0] <= center_x <= litter_box_coords[2] and
                    litter_box_coords[1] <= center_y <= litter_box_coords[3]):
                    motion_in_box = True
                    
                    # Draw bounding box (yellow for in litter box)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                    cv.putText(frame, 'In Litter Box', (x, y - 10),
                              cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                else:
                    # Draw bounding box (green for outside)
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # ========== DRAW LITTER BOX ZONE ==========
        # Draw litter box rectangle
        cv.rectangle(frame,
                    (litter_box_coords[0], litter_box_coords[1]),
                    (litter_box_coords[2], litter_box_coords[3]),
                    (0, 255, 0), 2)  # Green
        
        # Add label
        cv.putText(frame, 'Litter Box Zone',
                  (litter_box_coords[0], litter_box_coords[1] - 10),
                  cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # ========== LOG EVENTS ==========
        # TODO: Add your event logging logic here
        # For now, just print to console
        if motion_in_box:
            cv.putText(frame, "CAT IN LITTER BOX", (10, 30),
                      cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # ========== DISPLAY ==========
        if show_preview:
            cv.imshow('Litter Box Monitor', frame)
            
            # Optional: Show motion mask
            if config.get("debug", {}).get("show_mask_window", False):
                cv.imshow('Motion Mask', fg_mask)
        
        # ========== KEYBOARD CONTROLS ==========
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reset background model
            bg_subtractor = cv.createBackgroundSubtractorKNN(
                history=history,
                dist2Threshold=dist_threshold,
                detectShadows=detect_shadows
            )
            print("Background model reset")
    
    # ========== CLEANUP ==========
    cam.release()
    cv.destroyAllWindows()
    print("Monitoring stopped")

if __name__ == "__main__":
    main()