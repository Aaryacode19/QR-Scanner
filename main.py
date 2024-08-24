import cv2
from flask import Flask, Response, render_template
import pandas as pd
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0)
event_data = pd.read_csv('trial.csv')['id'].astype(str).values
display_duration = 2  
scanned_codes = {} 

def gen_frames():
    global scanned_codes

    while True:
        success, frame = camera.read()
        if not success:
            break

        qr_detector = cv2.QRCodeDetector()
        data, _, _ = qr_detector.detectAndDecode(frame)
        current_time = time.time()

        if data:
            if data in event_data and data not in scanned_codes:
                scanned_codes[data] = current_time  
                display_message = "Access Granted"
                display_color = (0, 255, 0)
            elif data in scanned_codes:
                if current_time - scanned_codes[data] > display_duration:
                    display_message = "Already Scanned"
                    display_color = (255, 255, 0)
            else:
                display_message = "Access Denied"
                display_color = (0, 0, 255)

            cv2.putText(frame, display_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, display_color, 2)

        # Convert frame to JPEG format and yield it to the browser
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
