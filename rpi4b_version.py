import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
import sys

# Try different camera backends for Raspberry Pi compatibility
def get_camera():
    # Try V4L2 first (works for most USB webcams)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if cap.isOpened():
        return cap
    # Try default backend
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        return cap
    # Try MMAL (for Pi Camera with legacy stack, rare)
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        if cap.isOpened():
            return cap
    except Exception:
        pass
    return None

cap = get_camera()

if not cap or not cap.isOpened():
    print("Error: Unable to access the camera. Try running 'libcamera-hello' to check camera status.")
    sys.exit(1)

# Tkinter window setup
root = tk.Tk()
root.title('OpenCV Live Feed in Tkinter')

# Main frame for layout
main_frame = tk.Frame(root)
main_frame.pack(fill='both', expand=True)

# Video frame on the left, anchored top-left
video_frame = tk.Frame(main_frame, width=480, height=360, bg='black')
video_frame.pack_propagate(False)  # Prevent frame from shrinking to fit contents
video_frame.pack(side=tk.LEFT, anchor='nw')

# Label for video frame (create after video_frame)
display = tk.Label(video_frame, bg='black')
display.pack(anchor='nw', fill='both', expand=True)

# Controls on the right
controls = tk.Frame(main_frame)
controls.pack(side=tk.LEFT, anchor='ne', padx=10, pady=10, fill='y')

# Variables for recording
recording = False
video_writer = None

# Take photo function
def take_photo():
    ret, frame = cap.read()
    if ret:
        filename = f"photo_{int(time.time())}.png"
        cv2.imwrite(filename, frame)
        print(f"Photo saved as {filename}")

# Record video toggle
def toggle_record():
    global recording, video_writer
    if not recording:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_writer = cv2.VideoWriter(f"video_{int(time.time())}.avi", fourcc, 20.0, (width, height))
        recording = True
        record_btn.config(text="Stop Recording")
        print("Recording started...")
    else:
        recording = False
        if video_writer:
            video_writer.release()
            video_writer = None
        record_btn.config(text="Record Video")
        print("Recording stopped.")

# Sliders for camera settings
def set_brightness(val):
    cap.set(cv2.CAP_PROP_BRIGHTNESS, float(val))
def set_contrast(val):
    cap.set(cv2.CAP_PROP_CONTRAST, float(val))
def set_exposure(val):
    cap.set(cv2.CAP_PROP_EXPOSURE, float(val))

# Get camera defaults for sliders
init_brightness = 128  # Adjusted for Raspberry Pi
init_contrast = 32     # Adjusted for Raspberry Pi
init_exposure = -4     # Adjusted for Raspberry Pi

photo_btn = tk.Button(controls, text="Take Photo", command=take_photo)
photo_btn.pack(fill='x', pady=2)
record_btn = tk.Button(controls, text="Record Video", command=toggle_record)
record_btn.pack(fill='x', pady=2)

brightness_slider = tk.Scale(controls, from_=0, to=255, orient='horizontal', label='Brightness', command=set_brightness, resolution=1)
brightness_slider.set(int(init_brightness))
brightness_slider.pack(fill='x', pady=2)

contrast_slider = tk.Scale(controls, from_=0, to=127, orient='horizontal', label='Contrast', command=set_contrast, resolution=1)
contrast_slider.set(int(init_contrast))
contrast_slider.pack(fill='x', pady=2)

exposure_slider = tk.Scale(controls, from_=-8, to=8, orient='horizontal', label='Exposure', command=set_exposure, resolution=0.1)
exposure_slider.set(float(init_exposure))
exposure_slider.pack(fill='x', pady=2)

# Clean up on close
def on_closing():
    if cap and cap.isOpened():
        cap.release()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', on_closing)

def update_frame():
    try:
        if not root.winfo_exists():
            return  # Window is closed, stop updating
        ret, frame = cap.read()
        if ret and frame is not None:
            # Resize frame to fit display area if needed
            frame = cv2.resize(frame, (480, 360))
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            display.imgtk = imgtk
            display.configure(image=imgtk)
            if recording and video_writer:
                video_writer.write(frame)
        else:
            # Show a black frame if no camera frame is available
            black_img = Image.new('RGB', (480, 360), 'black')
            imgtk = ImageTk.PhotoImage(image=black_img)
            display.imgtk = imgtk
            display.configure(image=imgtk)
        root.after(30, update_frame)
    except Exception as e:
        print(f"Error in update_frame: {e}")

# Start updating frames
update_frame()

root.mainloop()