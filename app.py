from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for storing attendance records
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        # Simulate biometric capture (you would use a fingerprint scanner or facial recognition here)
        student_id = request.form.get('student_id')

        # Save attendance to the database
        new_attendance = Attendance(
            student_id=student_id,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        db.session.add(new_attendance)
        db.session.commit()
        return redirect(url_for('attendance_list'))

    return render_template('mark_attendance.html')

@app.route('/attendance')
def attendance_list():
    attendances = Attendance.query.all()
    return render_template('attendance_list.html', attendances=attendances)

@app.route('/biometric_scan')
def biometric_scan():
    # This is where you'd trigger biometric scanning (fingerprint or facial recognition)
    # For facial recognition, let's use face_recognition library as an example
    
    # Load your pre-trained face data here (for facial recognition)
    # This can be a folder where you store images of registered faces
    known_faces = []  # List of known face encodings
    known_names = []  # Corresponding names

    # Example: Register a known face from an image
    known_image = face_recognition.load_image_file("known_face.jpg")
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    known_faces.append(known_face_encoding)
    known_names.append("John Doe")

    # Start video capture (this will open your webcam)
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()

        # Find all faces in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            # If recognized face is found, mark attendance
            if name != "Unknown":
                # Mark attendance in the system
                return redirect(url_for('mark_attendance', student_id=name))

        # Display the video feed
        cv2.imshow('Video', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close the windows
    video_capture.release()
    cv2.destroyAllWindows()

    return "Face Recognition Complete"

if __name__ == "__main__":
    app.run(debug=True)
