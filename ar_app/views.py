from django.shortcuts import render

# from cv2 import cv2 as cv2
import cv2
# import face_detection
from win11toast import toast
# import win11toast
import numpy as np
import mediapipe as mp
from django.http import StreamingHttpResponse
import threading
import time

def base(request):
    return render(request, 'base.html')

def face_detection(frame, face_mesh):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            ih, iw, _ = frame.shape
            min_x, min_y, max_x, max_y = iw, ih, 0, 0
            for landmark in face_landmarks.landmark:
                x, y = int(landmark.x * iw), int(landmark.y * ih)
                min_x, min_y = min(x, min_x), min(y, min_y)
                max_x, max_y = max(x, max_x), max(y, max_y)
            cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (255, 0, 255), 2)

    return frame

# def face_detection(frame, face_mesh):
#     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(frame_rgb)
#     if results.multi_face_landmarks:
#         for face_landmarks in results.multi_face_landmarks:
#             bboxC = face_landmarks.location_data.relative_bounding_box
#             ih, iw, _ = frame.shape
#             bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
#                    int(bboxC.width * iw), int(bboxC.height * ih)
#             cv2.rectangle(frame, bbox, (255, 0, 255), 2)

#     return frame



def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type="multipart/x-mixed-replace;boundary=frame")

def gen_frames():
    cap = cv2.VideoCapture(0)
    # .open(0)
    print(str(cap)+"Cap")
    cap.open(0)
    print("Id: "+ str(cap.getBackendName()))
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    # cap.set(3, 640)  # Set width
    # cap.set(4, 480)  # Set height

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
               max_num_faces=4,
               refine_landmarks=False,
               min_detection_confidence=0.5,
               min_tracking_confidence=0.5)
    print("Face mesh created: "+ str(face_mesh))
    try:
        while True:
            success, frame = cap.read()

            print("Facemesh: "+str(face_mesh) + "Success: " + str(success) +"\nRead: "+
                  str(cap.read()))
            if not success or frame is None:
                # toast("Failed to read Frame",duration = 'long')
                print("Error: Failed to read frame.")
                break
            
            print("Frame: "+str(frame))
            print("Hello")
            frame = face_detection(frame, face_mesh)
            print("Frame: "+str(frame))
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            print(str())

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cap.release()
        face_mesh.close()
        print("Facemesh released")
        cv2.destroyAllWindows()

def ar_view(request):
    return render(request, 'ar_view.html')

