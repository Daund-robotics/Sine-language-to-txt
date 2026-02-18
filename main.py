import cv2
import os
import pickle
import numpy as np
import sklearn
from sklearn.neighbors import KNeighborsClassifier

# Load data & Model
try:
    with open('gesture_data.pickle', 'rb') as f:
        data_dict = pickle.load(f)
    data = np.asarray(data_dict['data'])
    labels = np.asarray(data_dict['labels'])
    
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(data, labels)
    print("Model trained.")
except FileNotFoundError:
    print("Run data_creation.py first!")
    exit()

# Load Calibration
try:
    with open('hsv_values.pickle', 'rb') as f:
        hsv_range = pickle.load(f)
        lower, upper = hsv_range[0], hsv_range[1]
    print("Calibration loaded.")
except:
    print("Warning: No calibration found. Using defaults.")
    lower = np.array([0, 20, 70])
    upper = np.array([20, 255, 255])

# specific backend for windows
if os.name == 'nt':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)
background = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    H, W, _ = frame.shape
    
    x1, y1 = 300, 100
    x2, y2 = 600, 400
    
    roi = frame[y1:y2, x1:x2]
    
    # --- Background Subtraction ---
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray_roi = cv2.GaussianBlur(gray_roi, (7, 7), 0)

    if background is None:
        background = gray_roi.copy().astype("float")
    
    cv2.accumulateWeighted(gray_roi, background, 0.5)
    delta = cv2.absdiff(gray_roi, cv2.convertScaleAbs(background))
    thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    # ------------------------------

    # Process
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask_hsv = cv2.inRange(hsv, lower, upper)
    
    # Combine Masks
    combined_mask = cv2.bitwise_and(mask_hsv, thresh)
    
    mask = cv2.erode(combined_mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    blur = cv2.medianBlur(mask, 5)
    
    # Prediction
    resized = cv2.resize(blur, (50, 50))
    feature_vector = resized.flatten()
    
    label_text = ""
    # Features check
    if len(feature_vector) == data.shape[1]:
        prediction = model.predict([feature_vector])
        label_text = prediction[0]
    else:
        label_text = "Error: Dim Mismatch"

    # Visuals
    contours, _ = cv2.findContours(blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_contour) > 1000:
             hull = cv2.convexHull(max_contour)
             hull_shifted = hull + np.array([x1, y1])
             cnt_shifted = max_contour + np.array([x1, y1])
             cv2.drawContours(frame, [cnt_shifted], -1, (0, 0, 255), 2)
             cv2.drawContours(frame, [hull_shifted], -1, (0, 255, 255), 2)

    
    # Show text at bottom
    cv2.rectangle(frame, (0, H-80), (W, H), (0,0,0), -1)
    cv2.putText(frame, f"Prediction: {label_text}", (20, H-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, "Press 'r' to reset background", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Show mask
    mask_bgr = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
    mask_small = cv2.resize(mask_bgr, (150, 150))
    frame[0:150, 0:150] = mask_small

    cv2.imshow('Gesture Recognition', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break
    elif key == ord('r') or key == ord('R'):
        background = None
        print("Background Reset")

cap.release()
cv2.destroyAllWindows()

