
"""
SIGNIFICANCE:
This module handles the 'Vision' capability for SIRKIT.
It uses OpenCV to interface with local webcams, capture frames, 
and save them to the persistent data store.
"""

import cv2
import os
import datetime
import config
import time

class CameraEngine:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start_session(self):
        """Starts a persistent camera session."""
        if self.cap and self.cap.isOpened():
            return True
        
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("(!) Camera error: Could not open video device.")
            self.cap = None
            return False
        
        # Warmup
        for _ in range(5):
            self.cap.read()
        return True

    def stop_session(self):
        """Stops the persistent camera session."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def capture_image(self):
        """Captures a single frame. Uses session if active, else one-off."""
        if self.cap and self.cap.isOpened():
            # Use existing session - fast!
            ret, frame = self.cap.read()
            if not ret: return None
            return frame
        else:
            # One-off capture (fallback)
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened(): return None
            
            # Warmup
            for _ in range(10): cap.read()
            
            ret, frame = cap.read()
            cap.release()
            return frame if ret else None

    def save_image(self, frame):
        """Saves the given frame to disk with a timestamp."""
        if frame is None: return None
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(config.TESTER_DIR, filename)
        
        try:
            cv2.imwrite(filepath, frame)
            # Ensure it's readable
            return filepath
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

if __name__ == "__main__":
    cam = CameraEngine()
    print("Taking test picture...")
    frame = cam.capture_image()
    path = cam.save_image(frame)
    if path:
        print(f"Saved to: {path}")
