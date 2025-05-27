import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

# OpenCV video capture
cap = cv2.VideoCapture(0)

# Tkinter window setup
root = tk.Tk()
root.title('OpenCV Live Feed in Tkinter')

# Main frame for layout
main_frame = tk.Frame(root)
main_frame.pack(fill='both', expand=True)

# Video frame on the left, anchored top-left
video_frame = tk.Frame(main_frame)
video_frame.pack(side=tk.LEFT, anchor='nw')

# Label for video frame (create after video_frame)
display = tk.Label(video_frame)
display.pack(anchor='nw')

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
init_brightness = 255
init_contrast = 92
init_exposure = -1.9

# Use more typical value ranges for sliders
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
    cap.release()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', on_closing)

def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        display.imgtk = imgtk
        display.configure(image=imgtk)
        if recording and video_writer:
            video_writer.write(frame)
    root.after(10, update_frame)

# Start updating frames
update_frame()

root.mainloop()