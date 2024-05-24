import cv2
from cvzone.HandTrackingModule import HandDetector
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from pynput.keyboard import Key, Controller

# Initialize the hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 600)
cap.set(4, 400)

# Initialize keyboard controller
keyboard = Controller()

# Initialize the GUI
root = tk.Tk()
root.title("Hand Gesture Control")
root.geometry("800x600")

# Global variable to track if a hand is detected
hand_detected = False
current_fingers = -1  # to track the current gesture

def show_about():
    """Show the About dialog."""
    messagebox.showinfo("About", "Hand Gesture Control using OpenCV.\nDeveloped by Group 5")

def on_closing():
    """Release resources and close the application."""
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

# Style configuration
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 16))
style.configure("TButton", font=("Helvetica", 14), padding=10)

# GUI components
label = ttk.Label(root, text="Hand Gesture Control", style="TLabel")
label.pack(pady=10)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

about_button = ttk.Button(button_frame, text="About", command=show_about, style="TButton")
about_button.grid(row=0, column=0, padx=5)

quit_button = ttk.Button(button_frame, text="Quit", command=on_closing, style="TButton")
quit_button.grid(row=0, column=1, padx=5)

video_label = ttk.Label(root)
video_label.pack(padx=10, pady=10)

def capture_video():
    """Capture video frames and process hand gestures."""
    global hand_detected, current_fingers

    success, img = cap.read()
    if not success:
        print("Failed to capture image from camera.")
        root.after(10, capture_video)
        return

    img = cv2.flip(img, 1)

    # Detect hand
    hands, img = detector.findHands(img)
    
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        totalFingers = fingers.count(1)
        cv2.putText(img, f'Fingers: {totalFingers}', (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        if not hand_detected or current_fingers != totalFingers:
            hand_detected = True
            current_fingers = totalFingers

            # Release all keys before pressing the new key
            keyboard.release(Key.right)
            keyboard.release(Key.left)
            keyboard.release(Key.enter)
            keyboard.release(Key.down)
            keyboard.release(Key.esc)

            # Gesture commands for Hill Climb Racing and other controls
            if totalFingers == 5:
                keyboard.press(Key.right)  # Accelerate
            elif totalFingers == 0:
                keyboard.press(Key.left)  # Brake
            elif totalFingers == 1:
                keyboard.press(Key.enter)  # Pause/Unpause
            elif totalFingers == 2:
                keyboard.press(Key.down)  # Up
            elif totalFingers == 3:
                keyboard.press(Key.esc)  # Down
    else:
        if hand_detected:
            keyboard.release(Key.right)
            keyboard.release(Key.left)
            keyboard.release(Key.enter)
            keyboard.release(Key.esc)
            keyboard.release(Key.down)
            hand_detected = False
            current_fingers = -1

    # Convert image to PhotoImage
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    
    # Update the video label
    video_label.imgtk = img_tk
    video_label.configure(image=img_tk)

    # Call this function again to create a loop
    root.after(10, capture_video)

# Start the video capture loop
capture_video()

# Start the GUI loop
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()