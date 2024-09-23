from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import cv2
import math as m
import mediapipe as mp
import time

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    # Get today's date
    today = datetime.today().date()
    
    # Set the reference date
    reference_date = datetime(2024, 9, 1).date()
    
    # Calculate the difference in days
    days_difference = (today - reference_date).days
    
    return render_template('index.html', my_days=days_difference)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/dailyTasks')
def task():
    return render_template('dailyTasks.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    message = None  # Initialize message variable
    if request.method == 'POST':
        if not os.path.exists('upload'):
            os.makedirs('upload')
        if not os.path.exists('output'):
            os.makedirs('output')

        # Save uploaded file
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join('upload', uploaded_file.filename)
            uploaded_file.save(file_path)

            # Process the video file
            output_file = process_video(file_path)

            # Pass the processed video to the processed_vid.html page
            message = "File uploaded and processed successfully!"  # Success message

    return render_template('upload.html', message=message)


def process_video(file_name):
    # Initialize frame counters
    good_frames = 0
    bad_frames = 0
    display_scale = 1
    font = cv2.FONT_HERSHEY_SIMPLEX
    green = (127, 255, 0)
    red = (50, 50, 255)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    file_path = file_name
    cap = cv2.VideoCapture(file_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    output_file_path = os.path.join('output', 'output_fullbody.mp4')
    video_output = cv2.VideoWriter(output_file_path, fourcc, fps, frame_size)

    # Initialize cumulative posture times
    cumulative_bad_time = 0
    cumulative_good_time = 0

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        h, w = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        keypoints = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        lm = keypoints.pose_landmarks
        lmPose = mp_pose.PoseLandmark

        bad_posture_detected = False
        good_posture_detected = False

        if lm:
            # Get coordinates of key landmarks for posture evaluation
            l_shldr_x = int(lm.landmark[lmPose.LEFT_SHOULDER].x * w)
            l_shldr_y = int(lm.landmark[lmPose.LEFT_SHOULDER].y * h)
            l_hip_x = int(lm.landmark[lmPose.LEFT_HIP].x * w)
            l_hip_y = int(lm.landmark[lmPose.LEFT_HIP].y * h)

            # Calculate angles for posture evaluation
            torso_inclination = findAngle(l_hip_x, l_hip_y, l_shldr_x, l_shldr_y)

            # Visualize landmarks and posture
            cv2.circle(image, (l_shldr_x, l_shldr_y), 7, yellow, -1)
            cv2.circle(image, (l_hip_x, l_hip_y), 7, yellow, -1)
            cv2.line(image, (l_shldr_x, l_shldr_y), (l_hip_x, l_hip_y), green, 4)

            angle_text_string = f'Torso Inclination: {int(torso_inclination)}'
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, green if torso_inclination < 10 else red, 2)

            # Check if the posture is good or bad
            if torso_inclination >= 10:
                bad_posture_detected = True
            else:
                good_posture_detected = True

            # Posture warnings and accumulate good/bad time
            if bad_posture_detected:
                bad_frames += 1  # Increment bad frames
            if good_posture_detected:
                good_frames += 1  # Increment good frames

            # Accumulate time based on posture detection
            bad_time = (1 / fps) * bad_frames
            good_time = (1 / fps) * good_frames

            if bad_posture_detected:
                cumulative_bad_time += (1 / fps)  # Accumulate bad time only when bad posture is detected
            if good_posture_detected:
                cumulative_good_time += (1 / fps)  # Accumulate good time only when good posture is detected

            # Display cumulative times on the video
            cv2.putText(image, f'Cumulative Bad Posture Time: {cumulative_bad_time:.2f}s', (10, 70), font, 0.8, red, 2)
            cv2.putText(image, f'Cumulative Good Posture Time: {cumulative_good_time:.2f}s', (10, 110), font, 0.8, green, 2)

            # Send warning if bad posture time exceeds a threshold (e.g., 180 seconds)
            if cumulative_bad_time > 180:
                sendWarning()

        # Resize and display the processed frame
        display_image = cv2.resize(image, (int(w * display_scale), int(h * display_scale)))
        video_output.write(image)
        cv2.imshow('MediaPipe Pose - Full Body', display_image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def sendWarning():
    print("Warning: Bad posture detected!")

def findDistance(x1, y1, x2, y2):
    dist = m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


# Calculate angle
def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = (180 / m.pi) * theta
    return degree


@app.route('/leaderboard')
def leaderboard():
    # Example leaderboard data (this could come from a database)
    leaderboard_data = [
        {"rank": 1, "name": "Alice", "score": 1200, "img": "alice.jpg"},
        {"rank": 2, "name": "Bob", "score": 1100, "img": "bob.jpg"},
        {"rank": 3, "name": "Charlie", "score": 1050, "img": "charlie.jpg"},
        {"rank": 4, "name": "Diana", "score": 950, "img": "diana.jpg"},
        {"rank": 5, "name": "Edward", "score": 900, "img": "edward.jpg"}
    ]
    
    top_3 = leaderboard_data[:3]

    return render_template('leaderboard.html', leaderboard=leaderboard_data, top_3=top_3)

@app.route('/myRewards')
def myRewards():
    return render_template('myRewards.html')

# Route to handle form submission or other POST requests
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form['data']
    # Process the data here
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0", debug=True)