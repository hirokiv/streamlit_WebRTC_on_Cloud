import cv2
import os
import face_recognition
import numpy as np

# Define the folder where known faces are stored
KNOWN_FACES_DIR = "images/known_faces"

def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    # Loop through each image file in the directory
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".jpeg", ".png")):  # Ensure it's an image file
            file_path = os.path.join(KNOWN_FACES_DIR, filename)

            # Load image and extract face encodings
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:  # Ensure at least one face was found
                encoding = encodings[0]  # Take the first face found
                known_face_encodings.append(encoding)

                # Extract name from filename (removing extension)
                name = os.path.splitext(filename)[0]
                known_face_names.append(name)

                print(f"Loaded face encoding for {name}")

    return known_face_encodings, known_face_names

# Call function to load faces
known_face_encodings, known_face_names = load_known_faces()

# # Mock database of known individuals (names and face encodings)
# known_face_encodings = []
# known_face_names = []
# 
# # Example: Person 1
# person1_image = face_recognition.load_image_file("images/known_faces/person1.jpg")
# person1_encoding = face_recognition.face_encodings(person1_image)[0]
# known_face_encodings.append(person1_encoding)
# known_face_names.append("Person One")
# 
# # Example: Person 2
# person2_image = face_recognition.load_image_file("images/known_faces/person2.jpg")
# person2_encoding = face_recognition.face_encodings(person2_image)[0]
# known_face_encodings.append(person2_encoding)
# known_face_names.append("Person Two")


# Load face detection model (Haar Cascade)
face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")

# Load emotion recognition model (FER+ ONNX model)
emotion_net = cv2.dnn.readNetFromONNX("models/emotion-ferplus-8.onnx")
# Define the list of emotion labels expected by the model output (indices 0-6 or 0-7 depending on the model)
emotion_labels = ['Neutral', 'Happy', 'Surprise', 'Sad', 'Anger', 'Disgust', 'Fear']
# (The FER+ model provides 7 or 8 emotions; here we use 7 common emotions&#8203;:contentReference[oaicite:6]{index=6})

# (Add more persons as needed)
def apply_face_recog(frame: np.ndarray) -> np.ndarray:
    """Detects faces in the frame, recognizes individuals, and predicts emotion.
       Draws bounding boxes and overlays name, emotion on the frame."""
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces in the frame (returns list of (x, y, w, h) for each face)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    # Convert frame to RGB once for face recognition (dlib uses RGB)
    rgb_frame = frame[:, :, ::1]  # or cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    for (x, y, w, h) in faces:
        # Coordinates for face region
        x1, y1, x2, y2 = x, y, x + w, y + h

        # 1. Face Recognition: Identify the person (if known)
        name = "Unknown"  # default name
        try:
            # Compute face encoding for the detected face
            face_encoding = face_recognition.face_encodings(rgb_frame, [(y1, x2, y2, x1)])[0]
            # Compare with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            # Use face distance to find the best match
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches and matches[best_match_index]:
                name = known_face_names[best_match_index]
        except IndexError:
            # If encoding fails (no face found by face_recognition in the region), skip recognition
            pass

        # 2. Emotion Detection: classify facial expression
        face_gray = gray[y1:y2, x1:x2]  # crop the face in grayscale
        # Preprocess for the emotion model: resize to 64x64 and reshape to network input shape
        face_gray_resized = cv2.resize(face_gray, (64, 64))
        # The FER+ ONNX model expects a 1x1x64x64 blob (1 batch, 1 channel, 64x64)
        blob = face_gray_resized.reshape(1, 1, 64, 64).astype('float32')
        emotion_net.setInput(blob)
        emotion_preds = emotion_net.forward()  # shape: (1, images/7) or (1, 8)
        emotion_id = int(np.argmax(emotion_preds))  # index of highest confidence
        emotion_label = emotion_labels[emotion_id] if emotion_id < len(emotion_labels) else "Unknown"

        # 3. Age Estimation: predict age range
        face_color = frame[y1:y2, x1:x2]  # crop the face in original color

        # 4. Draw bounding box and overlay text
        # Draw rectangle around face
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # Prepare label with name, emotion, age
        label = f"{name} ({emotion_label})"
        # Choose a position for the text: slightly above the top-left corner of the face rectangle
        text_y = y1 - 10 if y1 - 10 > 20 else y1 + 20  # if too close to top, put text below face
        cv2.putText(frame, label, (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8, color=(255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
    return frame
