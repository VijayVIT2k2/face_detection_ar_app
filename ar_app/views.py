from django.shortcuts import render
import cv2
import mediapipe as mp
from django.http import StreamingHttpResponse
import threading
import time

def base(request):
    return render(request, 'base.html')

def face_detection(frame, face_mesh):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                   int(bboxC.width * iw), int(bboxC.height * ih)
            cv2.rectangle(frame, bbox, (255, 0, 255), 2)

    return frame

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type="multipart/x-mixed-replace;boundary=frame")

def gen_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh()

    try:
        while True:
            success, frame = cap.read()
            if not success:
                print("Error: Failed to read frame.")
                break

            frame = face_detection(frame, face_mesh)

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cap.release()
        face_mesh.close()
        cv2.destroyAllWindows()

def ar_view(request):
    return render(request, 'ar_view.html')
