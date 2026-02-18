import cv2
import pickle
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# Global variables
data = []
labels = []
collecting = False
current_label = ""
hsv_lower = np.array([0, 20, 70])
hsv_upper = np.array([20, 255, 255])
background = None

class GestureApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Classifier for duplicate checking
        self.check_model = None
        self.train_check_model()

        self.window.bind('<q>', lambda event: self.on_closing())
        self.window.bind('<Q>', lambda event: self.on_closing())
        self.window.bind('<r>', lambda event: self.reset_background())
        self.window.bind('<R>', lambda event: self.reset_background())
        
        # Video source
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        # Main Layout
        self.main_frame = tk.Frame(window)
        self.main_frame.pack()

        # Canvas
        self.canvas = tk.Canvas(self.main_frame, width=640, height=480)
        self.canvas.pack(side=tk.LEFT)

        # Controls Panel
        self.controls_panel = tk.Frame(self.main_frame)
        self.controls_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Calibration Section
        tk.Label(self.controls_panel, text="Calibration (HSV)", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.sliders = {}
        for label, val, limit in [("H Min", 0, 179), ("S Min", 0, 255), ("V Min", 0, 255), 
                                  ("H Max", 179, 179), ("S Max", 255, 255), ("V Max", 255, 255)]:
            frame = tk.Frame(self.controls_panel)
            frame.pack()
            tk.Label(frame, text=label, width=5).pack(side=tk.LEFT)
            s = tk.Scale(frame, from_=0, to=limit, orient=tk.HORIZONTAL, length=150)
            s.set(val)
            s.pack(side=tk.LEFT)
            self.sliders[label] = s
        
        # Data Collection Section
        tk.Label(self.controls_panel, text="Data Collection", font=("Arial", 10, "bold")).pack(pady=10)
        
        self.lbl_entry = tk.Label(self.controls_panel, text="Label Name:")
        self.lbl_entry.pack()
        self.entry_label = tk.Entry(self.controls_panel)
        self.entry_label.pack(pady=5)

        self.btn_reset = tk.Button(self.controls_panel, text="Reset Background (R)", width=20, command=self.reset_background, bg="#ffffcc")
        self.btn_reset.pack(pady=5)

        self.btn_start = tk.Button(self.controls_panel, text="Start Capture", width=20, command=self.start_capture, bg="#dddddd")
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(self.controls_panel, text="Stop Capture", width=20, command=self.stop_capture, state=tk.DISABLED, bg="#ffcccc")
        self.btn_stop.pack(pady=5)

        self.btn_save = tk.Button(self.controls_panel, text="Save Data to File", width=20, command=self.save_data, bg="green", fg="white")
        self.btn_save.pack(pady=20)
        
        self.info_label = tk.Label(self.controls_panel, text="Prepare...", font=("Arial", 10))
        self.info_label.pack()

        self.load_hsv()

        self.match_text = "None"

        self.delay = 15
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_hsv(self):
        if os.path.exists('hsv_values.pickle'):
            try:
                with open('hsv_values.pickle', 'rb') as f:
                    vals = pickle.load(f)
                    self.sliders["H Min"].set(vals[0][0])
                    self.sliders["S Min"].set(vals[0][1])
                    self.sliders["V Min"].set(vals[0][2])
                    self.sliders["H Max"].set(vals[1][0])
                    self.sliders["S Max"].set(vals[1][1])
                    self.sliders["V Max"].set(vals[1][2])
            except:
                pass

    def save_hsv(self):
        lower = np.array([self.sliders["H Min"].get(), self.sliders["S Min"].get(), self.sliders["V Min"].get()])
        upper = np.array([self.sliders["H Max"].get(), self.sliders["S Max"].get(), self.sliders["V Max"].get()])
        with open('hsv_values.pickle', 'wb') as f:
            pickle.dump([lower, upper], f)

    def train_check_model(self):
        global data, labels
        if len(data) > 0:
            try:
                self.check_model = KNeighborsClassifier(n_neighbors=5)
                self.check_model.fit(data, labels)
            except Exception as e:
                print("Not enough data to train check model yet.")
                self.check_model = None
        else:
            self.check_model = None

    def start_capture(self):
        label = self.entry_label.get()
        if not label:
            messagebox.showwarning("Warning", "Please enter a label for this gesture!")
            return
        
        # Check for collision
        if self.check_model is not None and self.match_text != "None":
            if self.match_text != label:
                resp = messagebox.askyesno("Conflict Warning", 
                                           f"This gesture looks like '{self.match_text}'!\n\nAre you sure you want to label it as '{label}'?")
                if not resp:
                    return

        global collecting, current_label
        current_label = label
        collecting = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.entry_label.config(state=tk.DISABLED)
        self.info_label.config(text=f"Recording: {current_label}", fg="red")

    def stop_capture(self):
        global collecting
        collecting = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.entry_label.config(state=tk.NORMAL)
        self.info_label.config(text="Stopped.", fg="black")
        
        # Retrain check model with new data
        self.train_check_model()

    def reset_background(self):
        global background
        background = None
        self.info_label.config(text="Background Reset!", fg="blue")
        # Give user time to see message
        self.window.after(1000, lambda: self.info_label.config(text="Prepare...", fg="black"))

    def save_data(self):
        self.save_hsv()
        global data, labels
        if not data:
            messagebox.showwarning("Warning", "No data collected!")
            return

        try:
            with open('gesture_data.pickle', 'wb') as f:
                pickle.dump({'data': data, 'labels': labels}, f)
            messagebox.showinfo("Success", f"Saved {len(data)} samples!\nHSV Calibration also saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def update(self):
        global background
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.flip(frame, 1)
            H, W, _ = frame.shape
            
            x1, y1 = 300, 100
            x2, y2 = 600, 400
            
            roi = frame[y1:y2, x1:x2]
            
            # --- Background Subtraction Logic ---
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray_roi = cv2.GaussianBlur(gray_roi, (7, 7), 0)

            if background is None:
                background = gray_roi.copy().astype("float")
            
            cv2.accumulateWeighted(gray_roi, background, 0.5)
            delta = cv2.absdiff(gray_roi, cv2.convertScaleAbs(background))
            thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            # ------------------------------------

            # --- HSV Logic ---
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower = np.array([self.sliders["H Min"].get(), self.sliders["S Min"].get(), self.sliders["V Min"].get()])
            upper = np.array([self.sliders["H Max"].get(), self.sliders["S Max"].get(), self.sliders["V Max"].get()])
            
            mask_hsv = cv2.inRange(hsv, lower, upper)
            
            # Combine Masks
            combined_mask = cv2.bitwise_and(mask_hsv, thresh)
            
            mask = cv2.erode(combined_mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            blur = cv2.medianBlur(mask, 5)
            
            contours, _ = cv2.findContours(blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            found_hand = False
            feature_vector = None
            
            if contours:
                max_contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(max_contour) > 1000:
                    found_hand = True
                    rx, ry, rw, rh = cv2.boundingRect(max_contour)
                    
                    # Hull
                    hull = cv2.convexHull(max_contour)
                    hull_shifted = hull + np.array([x1, y1])
                    cnt_shifted = max_contour + np.array([x1, y1])
                    
                    cv2.drawContours(frame, [cnt_shifted], -1, (0, 0, 255), 2)
                    cv2.drawContours(frame, [hull_shifted], -1, (0, 255, 255), 2)
                    
                    # Prepare features
                    resized = cv2.resize(blur, (50, 50))
                    feature_vector = resized.flatten()

            # Collision Check
            self.match_text = "None"
            if self.check_model is not None and found_hand:
                try:
                    pred = self.check_model.predict([feature_vector])
                    self.match_text = pred[0]
                    
                    # Draw match on screen
                    cv2.putText(frame, f"Similiar to: {self.match_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                except:
                    pass

            mask_bgr = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
            mask_small = cv2.resize(mask_bgr, (150, 150))
            frame[0:150, 0:150] = mask_small
            cv2.putText(frame, "Combined Mask", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            if collecting and found_hand:
                data.append(feature_vector)
                labels.append(current_label)
                
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def on_closing(self):
        self.save_hsv()
        if self.vid.isOpened():
            self.vid.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureApp(root, "Gesture Tracker (Calibrate, Capture & Warn)")
    root.mainloop()
